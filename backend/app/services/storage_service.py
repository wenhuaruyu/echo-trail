import re
import uuid
from io import BytesIO
from pathlib import Path
from typing import Dict

from PIL import Image, ImageOps, UnidentifiedImageError

from app.core.config import settings
from app.core.errors import AppError


PHOTO_PATH = "/media/ticket-photos/"
PHOTO_NAME_PATTERN = re.compile(r"^[0-9a-f]{32}\.webp$")


class LocalPhotoStorage:
    def __init__(self) -> None:
        self.directory = Path(settings.media_root).resolve() / "ticket-photos"
        self.directory.mkdir(parents=True, exist_ok=True)

    def save_image(self, content: bytes) -> Dict[str, object]:
        if len(content) > settings.max_upload_size_bytes:
            raise AppError(413, "UPLOAD_TOO_LARGE", "图片不能超过{}MB".format(settings.max_upload_size_mb))
        try:
            Image.MAX_IMAGE_PIXELS = settings.max_image_pixels
            with Image.open(BytesIO(content)) as source:
                if source.format not in {"JPEG", "PNG", "WEBP"}:
                    raise AppError(415, "UPLOAD_TYPE_NOT_SUPPORTED", "仅支持JPEG、PNG和WebP图片")
                source.verify()
            with Image.open(BytesIO(content)) as source:
                image = ImageOps.exif_transpose(source)
                if image.width * image.height > settings.max_image_pixels:
                    raise AppError(413, "UPLOAD_PIXEL_LIMIT_EXCEEDED", "图片像素过大")
                image = image.convert("RGB")
                image.thumbnail((settings.max_image_edge, settings.max_image_edge), Image.Resampling.LANCZOS)
                filename = "{}.webp".format(uuid.uuid4().hex)
                path = self.directory / filename
                image.save(path, format="WEBP", quality=85, method=6, exif=b"")
                width, height = image.size
        except AppError:
            raise
        except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError):
            raise AppError(415, "UPLOAD_TYPE_NOT_SUPPORTED", "文件不是有效的受支持图片")

        return {
            "photo_url": "{}{}{}".format(settings.public_base_url.rstrip("/"), PHOTO_PATH, filename),
            "width": width,
            "height": height,
            "format": "webp",
            "size_bytes": path.stat().st_size,
        }

    def owns_photo_url(self, photo_url: str) -> bool:
        prefix = "{}{}".format(settings.public_base_url.rstrip("/"), PHOTO_PATH)
        if not photo_url.startswith(prefix):
            return False
        filename = photo_url[len(prefix):]
        if not PHOTO_NAME_PATTERN.fullmatch(filename):
            return False
        path = (self.directory / filename).resolve()
        return path.parent == self.directory and path.is_file()


photo_storage = LocalPhotoStorage()

