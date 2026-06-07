"""Deadlift-specific form rules and scoring penalties."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from app.domain.models import FormIssue, FrameMetrics, JointAngles, Landmark
from app.utils.landmarks import PoseLandmark
from app.utils.scoring import calculate_form_score

__all__ = ["calculate_form_score", "aggregate_issues", "evaluate_frame", "DeadliftThresholds"]


@dataclass(frozen=True)
class DeadliftThresholds:
    """Configurable thresholds for deadlift form analysis."""

    shoulders_forward_ratio: float = 0.06  # shoulders too far ahead of ankles
    rounded_back_shoulder_offset: float = 0.04  # shoulders ahead of hips when hinged
    min_hinge_torso_angle: float = 35.0  # need meaningful hinge to evaluate back
    max_hinge_torso_angle: float = 75.0  # excessive horizontal back at bottom
    min_lockout_knee_angle: float = 155.0
    min_lockout_hip_angle: float = 155.0


PENALTY_WEIGHTS = {
    "rounded_back": 25.0,
    "shoulders_too_far_forward": 15.0,
    "incomplete_lockout": 20.0,
}


def _get_landmark(landmarks: Sequence[Landmark], index: PoseLandmark) -> Landmark | None:
    if index >= len(landmarks):
        return None
    lm = landmarks[index]
    if lm.visibility < 0.5:
        return None
    return lm


def _midpoint(a: Landmark, b: Landmark) -> Landmark:
    return Landmark(
        x=(a.x + b.x) / 2,
        y=(a.y + b.y) / 2,
        z=(a.z + b.z) / 2,
        visibility=min(a.visibility, b.visibility),
    )


def check_shoulders_forward(
    landmarks: Sequence[Landmark],
    thresholds: DeadliftThresholds = DeadliftThresholds(),
) -> tuple[bool, dict]:
    """Shoulders should stay over the bar/feet, not drift far forward."""
    left_shoulder = _get_landmark(landmarks, PoseLandmark.LEFT_SHOULDER)
    right_shoulder = _get_landmark(landmarks, PoseLandmark.RIGHT_SHOULDER)
    left_ankle = _get_landmark(landmarks, PoseLandmark.LEFT_ANKLE)
    right_ankle = _get_landmark(landmarks, PoseLandmark.RIGHT_ANKLE)

    if not all((left_shoulder, right_shoulder, left_ankle, right_ankle)):
        return False, {"reason": "landmarks_not_visible"}

    shoulder_mid = _midpoint(left_shoulder, right_shoulder)  # type: ignore[arg-type]
    ankle_mid = _midpoint(left_ankle, right_ankle)  # type: ignore[arg-type]
    forward = shoulder_mid.x - ankle_mid.x
    too_far = forward > thresholds.shoulders_forward_ratio

    return too_far, {"shoulder_x": shoulder_mid.x, "ankle_x": ankle_mid.x, "forward_offset": forward}


def check_rounded_back(
    landmarks: Sequence[Landmark],
    torso_angle: float | None,
    thresholds: DeadliftThresholds = DeadliftThresholds(),
) -> tuple[bool, dict]:
    """
    Detect rounded back during hip hinge.

    Proxy: deep hinge (high torso angle) with shoulders shifted forward of hips.
    """
    if torso_angle is None or torso_angle < thresholds.min_hinge_torso_angle:
        return False, {"reason": "not_at_hinge_depth", "torso_angle": torso_angle}

    left_shoulder = _get_landmark(landmarks, PoseLandmark.LEFT_SHOULDER)
    right_shoulder = _get_landmark(landmarks, PoseLandmark.RIGHT_SHOULDER)
    left_hip = _get_landmark(landmarks, PoseLandmark.LEFT_HIP)
    right_hip = _get_landmark(landmarks, PoseLandmark.RIGHT_HIP)

    if not all((left_shoulder, right_shoulder, left_hip, right_hip)):
        return False, {"reason": "landmarks_not_visible"}

    shoulder_mid = _midpoint(left_shoulder, right_shoulder)  # type: ignore[arg-type]
    hip_mid = _midpoint(left_hip, right_hip)  # type: ignore[arg-type]
    shoulder_ahead = shoulder_mid.x - hip_mid.x

    rounded = (
        torso_angle > thresholds.max_hinge_torso_angle
        and shoulder_ahead > thresholds.rounded_back_shoulder_offset
    )

    return rounded, {
        "torso_angle": torso_angle,
        "shoulder_ahead_of_hip": shoulder_ahead,
    }


def check_incomplete_lockout(
    joint_angles: JointAngles,
    thresholds: DeadliftThresholds = DeadliftThresholds(),
) -> tuple[bool, dict]:
    """At lockout, hips and knees should be near full extension."""
    knee_vals = [v for v in (joint_angles.left_knee, joint_angles.right_knee) if v is not None]
    hip_vals = [v for v in (joint_angles.left_hip, joint_angles.right_hip) if v is not None]

    if not knee_vals or not hip_vals:
        return False, {"reason": "angles_not_measurable"}

    avg_knee = sum(knee_vals) / len(knee_vals)
    avg_hip = sum(hip_vals) / len(hip_vals)

    incomplete = avg_knee < thresholds.min_lockout_knee_angle or avg_hip < thresholds.min_lockout_hip_angle

    return incomplete, {"avg_knee": avg_knee, "avg_hip": avg_hip}


def evaluate_frame(
    frame_metrics: FrameMetrics,
    landmarks: Sequence[Landmark],
    thresholds: DeadliftThresholds = DeadliftThresholds(),
    at_lockout: bool = False,
) -> FrameMetrics:
    """Apply deadlift rules to a single frame."""
    shoulders_forward, shoulders_raw = check_shoulders_forward(landmarks, thresholds)
    rounded_back, back_raw = check_rounded_back(
        landmarks, frame_metrics.joint_angles.torso, thresholds
    )
    lockout_bad = False
    lockout_raw: dict = {"reason": "not_lockout_frame"}
    if at_lockout:
        lockout_bad, lockout_raw = check_incomplete_lockout(frame_metrics.joint_angles, thresholds)

    frame_metrics.flags = {
        "shoulders_too_far_forward": shoulders_forward,
        "rounded_back": rounded_back,
        "incomplete_lockout": lockout_bad,
    }
    frame_metrics.raw = {
        "shoulders_forward": shoulders_raw,
        "rounded_back": back_raw,
        "lockout": lockout_raw,
    }
    return frame_metrics


def lockout_frame_indices(frame_metrics: list[FrameMetrics], top_n: int = 3) -> set[int]:
    """Frames with most extended knees (likely lockout)."""
    scored: list[tuple[float, int]] = []
    for fm in frame_metrics:
        knee_vals = [
            v for v in (fm.joint_angles.left_knee, fm.joint_angles.right_knee) if v is not None
        ]
        if not knee_vals:
            continue
        scored.append((sum(knee_vals) / len(knee_vals), fm.frame_index))

    scored.sort(reverse=True)
    return {idx for _, idx in scored[:top_n]}


def aggregate_issues(frame_metrics_list: list[FrameMetrics]) -> list[FormIssue]:
    """Aggregate frame-level flags into form issues."""
    if not frame_metrics_list:
        return [
            FormIssue(
                issue="No pose detected",
                severity="high",
                feedback="Ensure your full body is visible in the frame.",
                penalty=100.0,
            )
        ]

    total = len(frame_metrics_list)
    counts = {
        "shoulders_too_far_forward": 0,
        "rounded_back": 0,
        "incomplete_lockout": 0,
    }

    for fm in frame_metrics_list:
        for key in counts:
            if fm.flags.get(key, False):
                counts[key] += 1

    ratios = {k: v / total for k, v in counts.items()}
    issues: list[FormIssue] = []

    if ratios["rounded_back"] > 0.25:
        severity = "high" if ratios["rounded_back"] > 0.5 else "medium"
        issues.append(
            FormIssue(
                issue="Rounded lower back",
                severity=severity,
                feedback="Brace your core and keep a neutral spine; chest up, hips back.",
                penalty=PENALTY_WEIGHTS["rounded_back"] * ratios["rounded_back"],
            )
        )

    if ratios["shoulders_too_far_forward"] > 0.25:
        severity = "medium" if ratios["shoulders_too_far_forward"] < 0.5 else "high"
        issues.append(
            FormIssue(
                issue="Shoulders drifting forward",
                severity=severity,
                feedback="Keep the bar close and shoulders over mid-foot.",
                penalty=PENALTY_WEIGHTS["shoulders_too_far_forward"] * ratios["shoulders_too_far_forward"],
            )
        )

    if ratios["incomplete_lockout"] > 0.2:
        severity = "medium"
        issues.append(
            FormIssue(
                issue="Incomplete lockout",
                severity=severity,
                feedback="Fully extend hips and knees at the top without leaning back excessively.",
                penalty=PENALTY_WEIGHTS["incomplete_lockout"] * ratios["incomplete_lockout"],
            )
        )

    return issues
