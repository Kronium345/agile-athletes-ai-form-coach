"""Squat-specific form rules and scoring penalties."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from app.domain.models import FormIssue, FrameMetrics, Landmark
from app.utils.landmarks import PoseLandmark


@dataclass(frozen=True)
class SquatThresholds:
    """Configurable thresholds for squat form analysis."""

    min_depth_ratio: float = 0.02  # image coords: hip below knee margin (normalized)
    min_depth_meters: float = 0.03  # world coords: hip below knee margin (meters)
    knee_valgus_ratio: float = 0.03  # knee medial to ankle-hip line
    max_torso_angle: float = 45.0  # degrees from vertical
    heel_lift_ratio: float = 0.015  # heel y above ankle y (image coords)
    heel_lift_meters: float = 0.02  # heel lift in world coords
    min_knee_angle_at_depth: float = 100.0  # below this = at depth


# Penalty weights (subtracted from 100)
PENALTY_WEIGHTS = {
    "insufficient_depth": 25.0,
    "knee_valgus": 20.0,
    "forward_lean": 15.0,
    "heel_lift": 10.0,
}


def _get_landmark(landmarks: Sequence[Landmark], index: PoseLandmark) -> Landmark | None:
    if index >= len(landmarks):
        return None
    lm = landmarks[index]
    if lm.visibility < 0.5:
        return None
    return lm


def check_depth(
    landmarks: Sequence[Landmark],
    thresholds: SquatThresholds = SquatThresholds(),
    world_landmarks: Sequence[Landmark] | None = None,
) -> tuple[bool, dict]:
    """
    Check if hip is below knee (good squat depth).

    Prefers world landmarks (meters, +Y up) when available for camera invariance.
    Falls back to normalized image coordinates where y increases downward.
    """
    if world_landmarks and len(world_landmarks) >= 33:
        return _check_depth_world(world_landmarks, thresholds)
    return _check_depth_image(landmarks, thresholds)


def _check_depth_image(
    landmarks: Sequence[Landmark],
    thresholds: SquatThresholds,
) -> tuple[bool, dict]:
    left_hip = _get_landmark(landmarks, PoseLandmark.LEFT_HIP)
    right_hip = _get_landmark(landmarks, PoseLandmark.RIGHT_HIP)
    left_knee = _get_landmark(landmarks, PoseLandmark.LEFT_KNEE)
    right_knee = _get_landmark(landmarks, PoseLandmark.RIGHT_KNEE)

    if not all((left_hip, right_hip, left_knee, right_knee)):
        return False, {"reason": "landmarks_not_visible", "coordinate_space": "image"}

    hip_y = (left_hip.y + right_hip.y) / 2  # type: ignore[union-attr]
    knee_y = (left_knee.y + right_knee.y) / 2  # type: ignore[union-attr]
    depth_achieved = hip_y > knee_y + thresholds.min_depth_ratio

    return depth_achieved, {
        "coordinate_space": "image",
        "hip_y": hip_y,
        "knee_y": knee_y,
        "depth_margin": hip_y - knee_y,
    }


def _check_depth_world(
    world_landmarks: Sequence[Landmark],
    thresholds: SquatThresholds,
) -> tuple[bool, dict]:
    """World coords: +Y is up, so hip below knee means hip.y < knee.y."""
    left_hip = _get_landmark(world_landmarks, PoseLandmark.LEFT_HIP)
    right_hip = _get_landmark(world_landmarks, PoseLandmark.RIGHT_HIP)
    left_knee = _get_landmark(world_landmarks, PoseLandmark.LEFT_KNEE)
    right_knee = _get_landmark(world_landmarks, PoseLandmark.RIGHT_KNEE)

    if not all((left_hip, right_hip, left_knee, right_knee)):
        return False, {"reason": "landmarks_not_visible", "coordinate_space": "world"}

    hip_y = (left_hip.y + right_hip.y) / 2  # type: ignore[union-attr]
    knee_y = (left_knee.y + right_knee.y) / 2  # type: ignore[union-attr]
    depth_achieved = hip_y < knee_y - thresholds.min_depth_meters

    return depth_achieved, {
        "coordinate_space": "world",
        "hip_y": hip_y,
        "knee_y": knee_y,
        "depth_margin": knee_y - hip_y,
    }


def check_knee_valgus(
    landmarks: Sequence[Landmark],
    side: str = "left",
    thresholds: SquatThresholds = SquatThresholds(),
) -> tuple[bool, dict]:
    """
    Detect inward knee collapse (valgus).

    Knee is valgus when it moves medially relative to the ankle-hip axis.
    For left leg: knee.x < ankle.x (knee inward toward center).
    For right leg: knee.x > ankle.x.
    """
    if side == "left":
        hip_idx, knee_idx, ankle_idx = (
            PoseLandmark.LEFT_HIP,
            PoseLandmark.LEFT_KNEE,
            PoseLandmark.LEFT_ANKLE,
        )
    else:
        hip_idx, knee_idx, ankle_idx = (
            PoseLandmark.RIGHT_HIP,
            PoseLandmark.RIGHT_KNEE,
            PoseLandmark.RIGHT_ANKLE,
        )

    hip = _get_landmark(landmarks, hip_idx)
    knee = _get_landmark(landmarks, knee_idx)
    ankle = _get_landmark(landmarks, ankle_idx)

    if not all((hip, knee, ankle)):
        return False, {"reason": "landmarks_not_visible"}

    # Expected knee x on hip-ankle line
    if abs(ankle.x - hip.x) < 1e-6:  # type: ignore[union-attr]
        expected_knee_x = hip.x  # type: ignore[union-attr]
    else:
        t = (knee.y - hip.y) / (ankle.y - hip.y)  # type: ignore[union-attr]
        t = max(0.0, min(1.0, t))
        expected_knee_x = hip.x + t * (ankle.x - hip.x)  # type: ignore[union-attr]

    if side == "left":
        valgus = knee.x < expected_knee_x - thresholds.knee_valgus_ratio  # type: ignore[union-attr]
        deviation = expected_knee_x - knee.x  # type: ignore[union-attr]
    else:
        valgus = knee.x > expected_knee_x + thresholds.knee_valgus_ratio  # type: ignore[union-attr]
        deviation = knee.x - expected_knee_x  # type: ignore[union-attr]

    return valgus, {
        "side": side,
        "knee_x": knee.x,  # type: ignore[union-attr]
        "expected_knee_x": expected_knee_x,
        "deviation": deviation,
    }


def check_forward_lean(
    torso_angle: float | None,
    thresholds: SquatThresholds = SquatThresholds(),
) -> tuple[bool, dict]:
    """Detect excessive forward torso lean."""
    if torso_angle is None:
        return False, {"reason": "torso_not_measurable"}

    excessive = torso_angle > thresholds.max_torso_angle
    return excessive, {"torso_angle": torso_angle}


def check_heel_lift(
    landmarks: Sequence[Landmark],
    side: str = "left",
    thresholds: SquatThresholds = SquatThresholds(),
) -> tuple[bool, dict]:
    """
    Detect heel lift (ankle instability).

    Heel lift when heel y is significantly above ankle y (smaller y = higher in frame).
    """
    if side == "left":
        ankle_idx, heel_idx = PoseLandmark.LEFT_ANKLE, PoseLandmark.LEFT_HEEL
    else:
        ankle_idx, heel_idx = PoseLandmark.RIGHT_ANKLE, PoseLandmark.RIGHT_HEEL

    ankle = _get_landmark(landmarks, ankle_idx)
    heel = _get_landmark(landmarks, heel_idx)

    if not all((ankle, heel)):
        return False, {"reason": "landmarks_not_visible"}

    # heel higher than ankle = heel.y < ankle.y - threshold
    lifted = heel.y < ankle.y - thresholds.heel_lift_ratio  # type: ignore[union-attr]

    return lifted, {
        "side": side,
        "heel_y": heel.y,  # type: ignore[union-attr]
        "ankle_y": ankle.y,  # type: ignore[union-attr]
        "lift_amount": ankle.y - heel.y,  # type: ignore[union-attr]
    }


def evaluate_frame(
    frame_metrics: FrameMetrics,
    landmarks: Sequence[Landmark],
    thresholds: SquatThresholds = SquatThresholds(),
    world_landmarks: Sequence[Landmark] | None = None,
) -> FrameMetrics:
    """Apply all squat rules to a single frame and populate flags."""
    depth_ok, depth_raw = check_depth(landmarks, thresholds, world_landmarks)
    left_valgus, left_valgus_raw = check_knee_valgus(landmarks, "left", thresholds)
    right_valgus, right_valgus_raw = check_knee_valgus(landmarks, "right", thresholds)
    forward_lean, lean_raw = check_forward_lean(frame_metrics.joint_angles.torso, thresholds)
    left_heel, left_heel_raw = check_heel_lift(landmarks, "left", thresholds)
    right_heel, right_heel_raw = check_heel_lift(landmarks, "right", thresholds)

    frame_metrics.flags = {
        "insufficient_depth": not depth_ok,
        "knee_valgus": left_valgus or right_valgus,
        "forward_lean": forward_lean,
        "heel_lift": left_heel or right_heel,
    }
    frame_metrics.raw = {
        "depth": depth_raw,
        "left_valgus": left_valgus_raw,
        "right_valgus": right_valgus_raw,
        "forward_lean": lean_raw,
        "left_heel": left_heel_raw,
        "right_heel": right_heel_raw,
    }
    return frame_metrics


def aggregate_issues(frame_metrics_list: list[FrameMetrics]) -> list[FormIssue]:
    """Aggregate frame-level flags into form issues with severity."""
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
        "insufficient_depth": 0,
        "knee_valgus": 0,
        "forward_lean": 0,
        "heel_lift": 0,
    }

    for fm in frame_metrics_list:
        for key in counts:
            if fm.flags.get(key, False):
                counts[key] += 1

    ratios = {k: v / total for k, v in counts.items()}
    issues: list[FormIssue] = []

    if ratios["insufficient_depth"] > 0.3:
        severity = "high" if ratios["insufficient_depth"] > 0.6 else "medium"
        issues.append(
            FormIssue(
                issue="Insufficient squat depth",
                severity=severity,
                feedback="Lower your hips until they are at or below knee level.",
                penalty=PENALTY_WEIGHTS["insufficient_depth"] * ratios["insufficient_depth"],
            )
        )

    if ratios["knee_valgus"] > 0.2:
        severity = "high" if ratios["knee_valgus"] > 0.5 else "medium"
        issues.append(
            FormIssue(
                issue="Knees collapsing inward",
                severity=severity,
                feedback="Push knees outward during descent.",
                penalty=PENALTY_WEIGHTS["knee_valgus"] * ratios["knee_valgus"],
            )
        )

    if ratios["forward_lean"] > 0.25:
        severity = "medium" if ratios["forward_lean"] < 0.5 else "high"
        issues.append(
            FormIssue(
                issue="Excessive forward lean",
                severity=severity,
                feedback="Keep chest up and core braced throughout the movement.",
                penalty=PENALTY_WEIGHTS["forward_lean"] * ratios["forward_lean"],
            )
        )

    if ratios["heel_lift"] > 0.15:
        severity = "low" if ratios["heel_lift"] < 0.3 else "medium"
        issues.append(
            FormIssue(
                issue="Heels lifting off ground",
                severity=severity,
                feedback="Keep heels planted; consider elevating heels or improving ankle mobility.",
                penalty=PENALTY_WEIGHTS["heel_lift"] * ratios["heel_lift"],
            )
        )

    return issues


def calculate_form_score(issues: list[FormIssue]) -> int:
    """Start at 100 and subtract weighted penalties."""
    score = 100.0
    for issue in issues:
        score -= issue.penalty
    return max(0, min(100, int(round(score))))
