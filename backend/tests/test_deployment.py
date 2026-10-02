from io import BytesIO

from PIL import Image

from app.core.config import Settings
from app.services.storage_service import CosPhotoStorage


class FakeCosClient:
    def __init__(self):
        self.objects = {}

    def put_object(self, Bucket, Body, Key, ContentType):
        self.objects[(Bucket, Key)] = (Body, ContentType)

    def head_object(self, Bucket, Key):
        if (Bucket, Key) not in self.objects:
            raise RuntimeError("not found")

    def head_bucket(self, Bucket):
        assert Bucket == "echo-trail-123456"


def make_png():
    output = BytesIO()
    Image.new("RGB", (20, 10), color=(35, 83, 67)).save(output, format="PNG")
    return output.getvalue()


def cos_settings():
    return Settings(
        _env_file=None,
        storage_backend="cos",
        cos_secret_id="test-id",
        cos_secret_key="test-key",
        cos_region="ap-guangzhou",
        cos_bucket="echo-trail-123456",
        cos_public_base_url="https://echo-trail-123456.cos.ap-guangzhou.myqcloud.com",
    )


def test_render_postgres_url_uses_psycopg_driver():
    configured = Settings(_env_file=None, database_url="postgresql://user:password@host/db")
    assert configured.sqlalchemy_database_url == "postgresql+psycopg://user:password@host/db"


def test_render_external_url_is_used_for_local_media(monkeypatch):
    monkeypatch.setenv("RENDER_EXTERNAL_URL", "https://echo-trail-api.onrender.com/")
    configured = Settings(_env_file=None, app_env="production")
    assert configured.effective_public_base_url == "https://echo-trail-api.onrender.com"


def test_cos_storage_uploads_and_owns_generated_photo():
    fake_client = FakeCosClient()
    storage = CosPhotoStorage(cos_settings(), client=fake_client)
    result = storage.save_image(make_png())

    assert result["photo_url"].startswith(cos_settings().cos_public_base_url + "/ticket-photos/")
    assert result["photo_url"].endswith(".webp")
    assert result["format"] == "webp"
    assert storage.owns_photo_url(result["photo_url"]) is True
    assert storage.owns_photo_url("https://example.com/photo.webp") is False
    assert storage.healthcheck() is True


def test_root_and_health_expose_deployment_status(client):
    root = client.get("/")
    assert root.status_code == 200
    assert root.json()["status"] == "running"
    assert root.headers["X-Request-ID"]

    health = client.get("/api/v1/health")
    assert health.status_code == 200
    assert health.json()["data"]["database"] == "connected"
    assert health.json()["data"]["storage"] == "connected"
