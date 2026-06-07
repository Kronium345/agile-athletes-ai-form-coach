"""Base class for exercise-specific form analyzers."""

from abc import ABC, abstractmethod

from app.domain.models import AnalysisResult, FrameLandmarks, FrameMetrics


class ExerciseAnalyzer(ABC):
    """Interface for exercise-specific form analysis."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Exercise identifier (e.g. 'squat')."""

    @abstractmethod
    def analyze(self, frames: list[FrameLandmarks]) -> AnalysisResult:
        """Analyze pose landmarks and return form assessment."""

    def compute_frame_metrics(self, frames: list[FrameLandmarks]) -> list[FrameMetrics]:
        """Default frame metrics computation; override if needed."""
        from app.utils.angle_calculator import calculate_all_joint_angles

        metrics: list[FrameMetrics] = []
        for frame in frames:
            if not frame.detected or not frame.landmarks:
                metrics.append(
                    FrameMetrics(
                        frame_index=frame.frame_index,
                        timestamp_ms=frame.timestamp_ms,
                        joint_angles=calculate_all_joint_angles([]),
                        flags={"no_detection": True},
                    )
                )
                continue

            angles = calculate_all_joint_angles(frame.landmarks)
            metrics.append(
                FrameMetrics(
                    frame_index=frame.frame_index,
                    timestamp_ms=frame.timestamp_ms,
                    joint_angles=angles,
                )
            )
        return metrics
