from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "寻声觅迹 API"
    app_env: str = "development"
    database_url: str = "sqlite:///./echo_trail.db"
    api_v1_prefix: str = "/api/v1"
    cors_origins: str = "http://localhost:3000,http://localhost:5173"
    media_root: str = "./media"
    public_base_url: str = "http://127.0.0.1:8000"
    max_upload_size_mb: int = 5
    max_image_pixels: int = 20_000_000
    max_image_edge: int = 2048

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origin_list(self) -> List[str]:
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]

    @property
    def max_upload_size_bytes(self) -> int:
        return self.max_upload_size_mb * 1024 * 1024


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
