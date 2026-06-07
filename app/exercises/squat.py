"""Squat form analyzer."""

from app.domain.models import AnalysisResult, FrameLandmarks, FrameMetrics, JointAngles
from app.exercises.base import ExerciseAnalyzer
from app.utils import exercise_rules
from app.utils.angle_calculator import calculate_all_joint_angles


class SquatAnalyzer(ExerciseAnalyzer):
    """Analyzes squat form using shared pose utilities and squat-specific rules."""

    @property
    def name(self) -> str:
        return "squat"

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
            exercise_rules.evaluate_frame(
                metrics, frame.landmarks, world_landmarks=frame.world_landmarks
            )
            frame_metrics.append(metrics)

        issues = exercise_rules.aggregate_issues(frame_metrics)
        score = exercise_rules.calculate_form_score(issues)
        joint_angles = self._summarize_joint_angles(frame_metrics)

        return AnalysisResult(
            exercise=self.name,
            score=score,
            issues=issues,
            joint_angles=joint_angles,
            frame_metrics=frame_metrics,
        )

    def _summarize_joint_angles(self, frame_metrics: list[FrameMetrics]) -> dict[str, float]:
        """Return representative joint angles from the deepest squat frame."""
        if not frame_metrics:
            return {}

        best: tuple[float, JointAngles] | None = None
        for fm in frame_metrics:
            angles = fm.joint_angles
            knee_vals = [v for v in (angles.left_knee, angles.right_knee) if v is not None]
            if not knee_vals:
                continue
            avg_knee = sum(knee_vals) / len(knee_vals)
            if best is None or avg_knee < best[0]:
                best = (avg_knee, angles)

        if best is None:
            return frame_metrics[-1].joint_angles.summary()

        return best[1].summary()
