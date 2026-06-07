"""Generic form analysis for exercises without specialized rules yet."""

from app.domain.models import AnalysisResult, FormIssue, FrameLandmarks, FrameMetrics
from app.exercises.base import ExerciseAnalyzer
from app.utils.angle_calculator import calculate_all_joint_angles
from app.utils import generic_rules


class GenericAnalyzer(ExerciseAnalyzer):
    """
    Fallback analyzer for any cataloged exercise.

    Provides pose visibility, range-of-motion, and stability scoring until
    an exercise-specific analyzer is implemented.
    """

    def __init__(self, exercise_id: str) -> None:
        self._exercise_id = exercise_id

    @property
    def name(self) -> str:
        return self._exercise_id

    def analyze(self, frames: list[FrameLandmarks]) -> AnalysisResult:
        detected_frames = [f for f in frames if f.detected and f.landmarks]
        frame_metrics: list[FrameMetrics] = []

        for frame in detected_frames:
            angles = calculate_all_joint_angles(frame.landmarks, frame.world_landmarks)
            metrics = FrameMetrics(
                frame_index=frame.frame_index,
                timestamp_ms=frame.timestamp_ms,
                joint_angles=angles,
            )
            generic_rules.evaluate_frame(metrics, len(detected_frames), len(frames))
            frame_metrics.append(metrics)

        issues = generic_rules.aggregate_issues(frame_metrics, len(frames))
        score = generic_rules.calculate_form_score(issues)
        joint_angles = generic_rules.summarize_joint_angles(frame_metrics)

        return AnalysisResult(
            exercise=self._exercise_id,
            score=score,
            issues=issues,
            joint_angles=joint_angles,
            frame_metrics=frame_metrics,
        )
