"""MediaPipe Pose Landmarker wrapper for frame-by-frame landmark extraction."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Iterator

import cv2
import mediapipe as mp
import numpy as np
from mediapipe.tasks import python as mp_python
from mediapipe.tasks.python import vision

from app.core.config import Settings
from app.domain.models import FrameLandmarks, Landmark
from app.utils.landmarks import NUM_LANDMARKS

logger = logging.getLogger(__name__)


class PoseDetector:
    """
    Extracts 33 pose landmarks from video frames using MediaPipe Pose Landmarker.

    Uses VIDEO running mode (detector-tracker pipeline) per MediaPipe guidance:
    detection runs on the first frame and when tracking is lost; subsequent
    frames are tracked for lower latency.

    Returns both normalized image landmarks and world landmarks (meters, hip origin).
    """

    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._landmarker = self._create_landmarker(settings)

    @staticmethod
    def _create_landmarker(settings: Settings) -> vision.PoseLandmarker:
        model_path = settings.pose_model_path
        if not model_path.exists():
            raise FileNotFoundError(
                f"Pose landmarker model not found at {model_path}. "
                "Run: python scripts/download_model.py"
            )

        base_options = mp_python.BaseOptions(model_asset_path=str(model_path))
        options = vision.PoseLandmarkerOptions(
            base_options=base_options,
            running_mode=vision.RunningMode.VIDEO,
            num_poses=settings.max_poses,
            min_pose_detection_confidence=settings.min_pose_detection_confidence,
            min_pose_presence_confidence=settings.min_pose_presence_confidence,
            min_tracking_confidence=settings.min_tracking_confidence,
        )
        return vision.PoseLandmarker.create_from_options(options)

    @staticmethod
    def _parse_landmarks(raw_landmarks: list) -> list[Landmark]:
        return [
            Landmark(
                x=lm.x,
                y=lm.y,
                z=lm.z,
                visibility=getattr(lm, "visibility", 1.0) or 1.0,
            )
            for lm in raw_landmarks[:NUM_LANDMARKS]
        ]

    def detect_frame(
        self,
        frame: np.ndarray,
        frame_index: int,
        timestamp_ms: int,
    ) -> FrameLandmarks:
        """Detect pose landmarks in a single BGR frame."""
        # BGR -> RGB (official MediaPipe preprocessing pattern)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb_frame)

        result = self._landmarker.detect_for_video(mp_image, timestamp_ms)

        if not result.pose_landmarks:
            return FrameLandmarks(
                frame_index=frame_index,
                timestamp_ms=timestamp_ms,
                landmarks=[],
                detected=False,
            )

        landmarks = self._parse_landmarks(result.pose_landmarks[0])
        world_landmarks: list[Landmark] = []
        if result.pose_world_landmarks:
            world_landmarks = self._parse_landmarks(result.pose_world_landmarks[0])

        return FrameLandmarks(
            frame_index=frame_index,
            timestamp_ms=timestamp_ms,
            landmarks=landmarks,
            world_landmarks=world_landmarks,
            detected=True,
        )

    def extract_from_video(
        self,
        video_path: Path,
        sample_every_n: int = 1,
    ) -> Iterator[FrameLandmarks]:
        """Extract landmarks from every (sampled) frame of a video file."""
        cap = cv2.VideoCapture(str(video_path))
        if not cap.isOpened():
            raise ValueError(f"Unable to open video: {video_path}")

        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        frame_index = 0
        processed = 0

        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                if frame_index % sample_every_n != 0:
                    frame_index += 1
                    continue

                timestamp_ms = int((frame_index / fps) * 1000)
                yield self.detect_frame(frame, frame_index, timestamp_ms)

                processed += 1
                frame_index += 1
        finally:
            cap.release()
            logger.info("Processed %d frames from %s", processed, video_path)

    def close(self) -> None:
        self._landmarker.close()

    def __enter__(self) -> PoseDetector:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()
