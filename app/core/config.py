from functools import lru_cache
from pathlib import Path
from typing import Annotated, Any

from pydantic import field_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "Agile Athletes AI Form Coach"
    app_version: str = "0.1.0"
    debug: bool = False

    # MediaPipe
    pose_model_path: Path = Path("models/pose_landmarker_lite.task")
    min_pose_detection_confidence: float = 0.5
    min_pose_presence_confidence: float = 0.5
    min_tracking_confidence: float = 0.5
    max_poses: int = 1

    # Video processing
    max_video_size_mb: int = 50
    sample_every_n_frames: int = 1

    # Metrics storage
    metrics_dir: Path = Path("data/metrics")

    # CORS (Expo dev client) — comma-separated in .env, e.g. CORS_ORIGINS=*
    cors_origins: Annotated[list[str], NoDecode] = ["*"]

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: Any) -> list[str]:
        if isinstance(value, str):
            return [origin.strip() for origin in value.split(",") if origin.strip()]
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
