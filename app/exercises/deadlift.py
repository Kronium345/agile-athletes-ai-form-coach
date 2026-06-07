"""Deadlift form analyzer."""

from app.domain.models import AnalysisResult, FrameLandmarks, FrameMetrics, JointAngles
from app.exercises.base import ExerciseAnalyzer
from app.utils import deadlift_rules
from app.utils.angle_calculator import calculate_all_joint_angles


class DeadliftAnalyzer(ExerciseAnalyzer):
    """Analyzes deadlift form using hip-hinge and lockout rules."""

    def __init__(self, exercise_id: str = "deadlift") -> None:
        self._exercise_id = exercise_id

    @property
    def name(self) -> str:
        return self._exercise_id

    def analyze(self, frames: list[FrameLandmarks]) -> AnalysisResult:
        detected_frames = [f for f in frames if f.detected and f.landmarks]
        frame_metrics: list[FrameMetrics] = []

        for frame in detected_frames:
            angles = calculate_all_joint_angles(frame.landmarks, frame.world_landmarks)
            frame_metrics.append(
                FrameMetrics(
                    frame_index=frame.frame_index,
                    timestamp_ms=frame.timestamp_ms,
                    joint_angles=angles,
                )
            )

        lockout_frames = deadlift_rules.lockout_frame_indices(frame_metrics)

        for i, frame in enumerate(detected_frames):
            at_lockout = frame.frame_index in lockout_frames
            deadlift_rules.evaluate_frame(
                frame_metrics[i], frame.landmarks, at_lockout=at_lockout
            )

        issues = deadlift_rules.aggregate_issues(frame_metrics)
        score = deadlift_rules.calculate_form_score(issues)
        joint_angles = self._summarize_joint_angles(frame_metrics)

        return AnalysisResult(
            exercise=self._exercise_id,
            score=score,
            issues=issues,
            joint_angles=joint_angles,
            frame_metrics=frame_metrics,
        )

    def _summarize_joint_angles(self, frame_metrics: list[FrameMetrics]) -> dict[str, float]:
        if not frame_metrics:
            return {}

        best: tuple[float, JointAngles] | None = None
        for fm in frame_metrics:
            torso = fm.joint_angles.torso
            if torso is None:
                continue
            if best is None or torso > best[0]:
                best = (torso, fm.joint_angles)

        if best is None:
            return frame_metrics[-1].joint_angles.summary()

        angles = best[1]
        result = angles.summary()
        if angles.torso is not None:
            result["torso"] = round(angles.torso, 1)
        return result
