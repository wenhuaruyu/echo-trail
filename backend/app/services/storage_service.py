import os
import re
import uuid
from io import BytesIO
from pathlib import Path
from typing import Dict, Optional, Tuple

from PIL import Image, ImageOps, UnidentifiedImageError

from app.core.config import Settings, settings
from app.core.errors import AppError


PHOTO_PATH = "/media/ticket-photos/"
COS_PHOTO_PREFIX = "ticket-photos/"
PHOTO_NAME_PATTERN = re.compile(r"^[0-9a-f]{32}\.webp$")


def process_image(content: bytes, app_settings: Settings = settings) -> Tuple[bytes, int, int]:
    if len(content) > app_settings.max_upload_size_bytes:
        raise AppError(413, "UPLOAD_TOO_LARGE", "图片不能超过{}MB".format(app_settings.max_upload_size_mb))
    try:
        Image.MAX_IMAGE_PIXELS = app_settings.max_image_pixels
        with Image.open(BytesIO(content)) as source:
            if source.format not in {"JPEG", "PNG", "WEBP"}:
                raise AppError(415, "UPLOAD_TYPE_NOT_SUPPORTED", "仅支持JPEG、PNG和WebP图片")
            source.verify()
        with Image.open(BytesIO(content)) as source:
            image = ImageOps.exif_transpose(source)
            if image.width * image.height > app_settings.max_image_pixels:
                raise AppError(413, "UPLOAD_PIXEL_LIMIT_EXCEEDED", "图片像素过大")
            image = image.convert("RGB")
            image.thumbnail((app_settings.max_image_edge, app_settings.max_image_edge), Image.Resampling.LANCZOS)
            output = BytesIO()
            # Method 4 keeps good ticket-photo quality while avoiding the much
            # slower maximum-effort WebP encode on small cloud instances.
            image.save(output, format="WEBP", quality=82, method=4, exif=b"")
            width, height = image.size
    except AppError:
        raise
    except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError):
        raise AppError(415, "UPLOAD_TYPE_NOT_SUPPORTED", "文件不是有效的受支持图片")
    return output.getvalue(), width, height


class LocalPhotoStorage:
    def __init__(self, app_settings: Settings = settings) -> None:
        self.settings = app_settings
        self.directory = Path(app_settings.media_root).resolve() / "ticket-photos"
        self.directory.mkdir(parents=True, exist_ok=True)

    def save_image(self, content: bytes) -> Dict[str, object]:
        encoded, width, height = process_image(content, self.settings)
        filename = "{}.webp".format(uuid.uuid4().hex)
        path = self.directory / filename
        path.write_bytes(encoded)
        return {
            "photo_url": "{}{}{}".format(self.settings.effective_public_base_url, PHOTO_PATH, filename),
            "width": width,
            "height": height,
            "format": "webp",
            "size_bytes": len(encoded),
        }

    def owns_photo_url(self, photo_url: str) -> bool:
        prefix = "{}{}".format(self.settings.effective_public_base_url, PHOTO_PATH)
        if not photo_url.startswith(prefix):
            return False
        filename = photo_url[len(prefix):]
        if not PHOTO_NAME_PATTERN.fullmatch(filename):
            return False
        path = (self.directory / filename).resolve()
        return path.parent == self.directory and path.is_file()

    def healthcheck(self) -> bool:
        return self.directory.is_dir() and os.access(str(self.directory), os.W_OK)


class CosPhotoStorage:
    def __init__(self, app_settings: Settings = settings, client=None) -> None:
        self.settings = app_settings
        required = {
            "COS_SECRET_ID": app_settings.cos_secret_id,
            "COS_SECRET_KEY": app_settings.cos_secret_key,
            "COS_REGION": app_settings.cos_region,
            "COS_BUCKET": app_settings.cos_bucket,
            "COS_PUBLIC_BASE_URL": app_settings.cos_public_base_url,
        }
        missing = [key for key, value in required.items() if not value.strip()]
        if missing:
            raise RuntimeError("COS存储缺少环境变量: {}".format(", ".join(missing)))
        self.public_base_url = app_settings.cos_public_base_url.rstrip("/")
        if client is None:
            from qcloud_cos import CosConfig, CosS3Client

            config = CosConfig(
                Region=app_settings.cos_region,
                SecretId=app_settings.cos_secret_id,
                SecretKey=app_settings.cos_secret_key,
                Scheme="https",
            )
            client = CosS3Client(config)
        self.client = client

    def save_image(self, content: bytes) -> Dict[str, object]:
        encoded, width, height = process_image(content, self.settings)
        key = "{}{}.webp".format(COS_PHOTO_PREFIX, uuid.uuid4().hex)
        self.client.put_object(
            Bucket=self.settings.cos_bucket,
            Body=encoded,
            Key=key,
            ContentType="image/webp",
        )
        return {
            "photo_url": "{}/{}".format(self.public_base_url, key),
            "width": width,
            "height": height,
            "format": "webp",
            "size_bytes": len(encoded),
        }

    def _key_from_url(self, photo_url: str) -> Optional[str]:
        prefix = "{}/{}".format(self.public_base_url, COS_PHOTO_PREFIX)
        if not photo_url.startswith(prefix):
            return None
        filename = photo_url[len(prefix):]
        if not PHOTO_NAME_PATTERN.fullmatch(filename):
            return None
        return "{}{}".format(COS_PHOTO_PREFIX, filename)

    def owns_photo_url(self, photo_url: str) -> bool:
        key = self._key_from_url(photo_url)
        if key is None:
            return False
        try:
            self.client.head_object(Bucket=self.settings.cos_bucket, Key=key)
            return True
        except Exception:
            return False

    def healthcheck(self) -> bool:
        try:
            self.client.head_bucket(Bucket=self.settings.cos_bucket)
            return True
        except Exception:
            return False


def build_photo_storage(app_settings: Settings = settings):
    if app_settings.normalized_storage_backend == "local":
        return LocalPhotoStorage(app_settings)
    if app_settings.normalized_storage_backend == "cos":
        return CosPhotoStorage(app_settings)
    raise RuntimeError("STORAGE_BACKEND只能是local或cos")


photo_storage = build_photo_storage()
