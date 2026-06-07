"""Generic pose-quality rules for exercises without specialized analyzers."""

from app.domain.models import FormIssue, FrameMetrics
from app.utils.scoring import calculate_form_score

PENALTY_WEIGHTS = {
    "pose_not_detected": 40.0,
    "limited_visibility": 20.0,
    "limited_range_of_motion": 15.0,
}


def evaluate_frame(
    frame_metrics: FrameMetrics,
    detected_count: int,
    total_count: int,
) -> FrameMetrics:
    """Flag generic quality signals on a detected frame."""
    angles = frame_metrics.joint_angles
    measurable = sum(
        1
        for v in (
            angles.left_knee,
            angles.right_knee,
            angles.left_hip,
            angles.right_hip,
            angles.torso,
        )
        if v is not None
    )

    frame_metrics.flags = {
        "low_joint_data": measurable < 3,
    }
    frame_metrics.raw = {
        "measurable_angles": measurable,
        "detection_ratio": detected_count / total_count if total_count else 0,
    }
    return frame_metrics


def _movement_range(frame_metrics: list[FrameMetrics]) -> float:
    """Average joint angle range across frames — proxy for ROM."""
    series: dict[str, list[float]] = {}
    for fm in frame_metrics:
        for key, val in fm.joint_angles.to_dict().items():
            series.setdefault(key, []).append(val)

    ranges = [max(vals) - min(vals) for vals in series.values() if len(vals) >= 2]
    if not ranges:
        return 0.0
    return sum(ranges) / len(ranges)


def aggregate_issues(
    frame_metrics: list[FrameMetrics],
    total_frames: int,
) -> list[FormIssue]:
    if total_frames == 0:
        return [
            FormIssue(
                issue="No video frames processed",
                severity="high",
                feedback="Upload a valid exercise video.",
                penalty=100.0,
            )
        ]

    if not frame_metrics:
        return [
            FormIssue(
                issue="No pose detected",
                severity="high",
                feedback="Ensure your full body is visible with good lighting.",
                penalty=100.0,
            )
        ]

    detection_ratio = len(frame_metrics) / total_frames
    low_data_frames = sum(1 for fm in frame_metrics if fm.flags.get("low_joint_data"))
    low_data_ratio = low_data_frames / len(frame_metrics)
    rom = _movement_range(frame_metrics)

    issues: list[FormIssue] = []

    if detection_ratio < 0.5:
        issues.append(
            FormIssue(
                issue="Pose frequently lost",
                severity="high",
                feedback="Keep your full body in frame throughout the entire rep.",
                penalty=PENALTY_WEIGHTS["pose_not_detected"] * (1 - detection_ratio),
            )
        )

    if low_data_ratio > 0.4:
        issues.append(
            FormIssue(
                issue="Limited body visibility",
                severity="medium",
                feedback="Improve camera angle and lighting so joints stay visible.",
                penalty=PENALTY_WEIGHTS["limited_visibility"] * low_data_ratio,
            )
        )

    if rom < 15.0 and detection_ratio >= 0.5:
        issues.append(
            FormIssue(
                issue="Limited range of motion detected",
                severity="low",
                feedback="Use a full range of motion or film a clearer side angle.",
                penalty=PENALTY_WEIGHTS["limited_range_of_motion"],
            )
        )

    if not issues:
        issues.append(
            FormIssue(
                issue="General form looks stable",
                severity="low",
                feedback=(
                    "Pose tracking succeeded. Specialized coaching for this exercise "
                    "is coming soon — squat and deadlift have detailed analysis today."
                ),
                penalty=0.0,
            )
        )

    return issues


def summarize_joint_angles(frame_metrics: list[FrameMetrics]) -> dict[str, float]:
    if not frame_metrics:
        return {}

    mid = frame_metrics[len(frame_metrics) // 2]
    result = mid.joint_angles.summary()
    if mid.joint_angles.torso is not None:
        result["torso"] = round(mid.joint_angles.torso, 1)
    return result
