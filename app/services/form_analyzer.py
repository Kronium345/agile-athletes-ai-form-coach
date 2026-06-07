"""Orchestrates video analysis pipeline."""

from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path

from app.core.config import Settings
from app.domain.models import AnalysisResult, FrameLandmarks
from app.exercises.registry import ExerciseRegistry
from app.services.video_processor import save_upload_to_temp, validate_video_file
from app.utils.pose_detector import PoseDetector

logger = logging.getLogger(__name__)


class FormAnalyzerService:
    """High-level service for analyzing exercise form from video uploads."""

    def __init__(
        self,
        settings: Settings,
        pose_detector: PoseDetector,
        registry: ExerciseRegistry,
    ) -> None:
        self._settings = settings
        self._pose_detector = pose_detector
        self._registry = registry

    def analyze_video(
        self,
        video_bytes: bytes,
        exercise: str = "squat",
        filename: str = "upload.mp4",
    ) -> AnalysisResult:
        suffix = Path(filename).suffix or ".mp4"
        temp_path = save_upload_to_temp(video_bytes, suffix=suffix)

        try:
            validate_video_file(temp_path, self._settings.max_video_size_mb)
            frames = list(
                self._pose_detector.extract_from_video(
                    temp_path,
                    sample_every_n=self._settings.sample_every_n_frames,
                )
            )
            analyzer = self._registry.get(exercise)
            result = analyzer.analyze(frames)
            result.metrics_file = self._save_frame_metrics(result, exercise)
            return result
        finally:
            temp_path.unlink(missing_ok=True)

    def _save_frame_metrics(
        self,
        result: AnalysisResult,
        exercise: str,
    ) -> str | None:
        """Persist frame-by-frame metrics to disk."""
        if not result.frame_metrics:
            return None

        metrics_dir = self._settings.metrics_dir
        metrics_dir.mkdir(parents=True, exist_ok=True)

        session_id = uuid.uuid4().hex[:12]
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        filename = f"{exercise}_{timestamp}_{session_id}.json"
        filepath = metrics_dir / filename

        payload = {
            "exercise": result.exercise,
            "score": result.score,
            "saved_at": datetime.now(timezone.utc).isoformat(),
            "frames": [
                {
                    "frame_index": fm.frame_index,
                    "timestamp_ms": fm.timestamp_ms,
                    "joint_angles": fm.joint_angles.to_dict(),
                    "flags": fm.flags,
                }
                for fm in result.frame_metrics
            ],
        }

        filepath.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        logger.info("Saved frame metrics to %s", filepath)
        return str(filepath)
