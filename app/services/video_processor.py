"""Video file handling utilities."""

import logging
import tempfile
from pathlib import Path

import cv2

logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {".mp4", ".mov", ".avi", ".mkv"}


def validate_video_file(path: Path, max_size_mb: int = 50) -> None:
    """Validate video file exists, has allowed extension, and is within size limit."""
    if not path.exists():
        raise ValueError("Video file not found")

    if path.suffix.lower() not in ALLOWED_EXTENSIONS:
        raise ValueError(
            f"Unsupported video format '{path.suffix}'. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    size_mb = path.stat().st_size / (1024 * 1024)
    if size_mb > max_size_mb:
        raise ValueError(f"Video exceeds maximum size of {max_size_mb} MB")

    cap = cv2.VideoCapture(str(path))
    if not cap.isOpened():
        cap.release()
        raise ValueError("Unable to read video file")
    cap.release()


def save_upload_to_temp(content: bytes, suffix: str = ".mp4") -> Path:
    """Persist uploaded bytes to a temporary file."""
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    try:
        tmp.write(content)
        tmp.flush()
        return Path(tmp.name)
    finally:
        tmp.close()
