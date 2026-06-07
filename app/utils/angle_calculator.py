"""Calculate joint angles from three landmarks."""

import math
from typing import Sequence

from app.domain.models import Landmark, JointAngles
from app.utils.landmarks import NUM_LANDMARKS, PoseLandmark


def _landmark(
    landmarks: Sequence[Landmark],
    index: PoseLandmark | int,
) -> Landmark | None:
    if index < 0 or index >= len(landmarks):
        return None
    lm = landmarks[index]
    if lm.visibility < 0.5:
        return None
    return lm


def _has_world_landmarks(world_landmarks: Sequence[Landmark] | None) -> bool:
    return world_landmarks is not None and len(world_landmarks) >= NUM_LANDMARKS


def _select_landmarks(
    landmarks: Sequence[Landmark],
    world_landmarks: Sequence[Landmark] | None,
) -> tuple[Sequence[Landmark], bool]:
    """Prefer world landmarks for metric analysis when available."""
    if _has_world_landmarks(world_landmarks):
        return world_landmarks, True  # type: ignore[return-value]
    return landmarks, False


def calculate_angle(
    point_a: Landmark,
    point_b: Landmark,
    point_c: Landmark,
) -> float:
    """
    Calculate the angle at point_b formed by point_a -> point_b -> point_c.

    Returns angle in degrees (0-180) using 2D image-plane coordinates.
    """
    ba = (point_a.x - point_b.x, point_a.y - point_b.y)
    bc = (point_c.x - point_b.x, point_c.y - point_b.y)

    dot = ba[0] * bc[0] + ba[1] * bc[1]
    mag_ba = math.hypot(ba[0], ba[1])
    mag_bc = math.hypot(bc[0], bc[1])

    if mag_ba == 0 or mag_bc == 0:
        return 0.0

    cos_angle = max(-1.0, min(1.0, dot / (mag_ba * mag_bc)))
    return math.degrees(math.acos(cos_angle))


def calculate_angle_3d(
    point_a: Landmark,
    point_b: Landmark,
    point_c: Landmark,
) -> float:
    """
    Calculate 3D joint angle using world landmarks (meters).

    More camera-angle invariant than 2D image-plane angles.
    """
    ba = (point_a.x - point_b.x, point_a.y - point_b.y, point_a.z - point_b.z)
    bc = (point_c.x - point_b.x, point_c.y - point_b.y, point_c.z - point_b.z)

    dot = ba[0] * bc[0] + ba[1] * bc[1] + ba[2] * bc[2]
    mag_ba = math.sqrt(ba[0] ** 2 + ba[1] ** 2 + ba[2] ** 2)
    mag_bc = math.sqrt(bc[0] ** 2 + bc[1] ** 2 + bc[2] ** 2)

    if mag_ba == 0 or mag_bc == 0:
        return 0.0

    cos_angle = max(-1.0, min(1.0, dot / (mag_ba * mag_bc)))
    return math.degrees(math.acos(cos_angle))


def _joint_angle(
    landmarks: Sequence[Landmark],
    a: PoseLandmark,
    b: PoseLandmark,
    c: PoseLandmark,
    use_3d: bool,
) -> float | None:
    p_a = _landmark(landmarks, a)
    p_b = _landmark(landmarks, b)
    p_c = _landmark(landmarks, c)
    if not all((p_a, p_b, p_c)):
        return None
    if use_3d:
        return calculate_angle_3d(p_a, p_b, p_c)  # type: ignore[arg-type]
    return calculate_angle(p_a, p_b, p_c)  # type: ignore[arg-type]


def calculate_knee_angle(
    landmarks: Sequence[Landmark],
    side: str = "left",
    world_landmarks: Sequence[Landmark] | None = None,
) -> float | None:
    """Knee angle: hip -> knee -> ankle."""
    source, use_3d = _select_landmarks(landmarks, world_landmarks)
    if side == "left":
        return _joint_angle(
            source, PoseLandmark.LEFT_HIP, PoseLandmark.LEFT_KNEE, PoseLandmark.LEFT_ANKLE, use_3d
        )
    return _joint_angle(
        source, PoseLandmark.RIGHT_HIP, PoseLandmark.RIGHT_KNEE, PoseLandmark.RIGHT_ANKLE, use_3d
    )


def calculate_hip_angle(
    landmarks: Sequence[Landmark],
    side: str = "left",
    world_landmarks: Sequence[Landmark] | None = None,
) -> float | None:
    """Hip angle: shoulder -> hip -> knee."""
    source, use_3d = _select_landmarks(landmarks, world_landmarks)
    if side == "left":
        return _joint_angle(
            source,
            PoseLandmark.LEFT_SHOULDER,
            PoseLandmark.LEFT_HIP,
            PoseLandmark.LEFT_KNEE,
            use_3d,
        )
    return _joint_angle(
        source,
        PoseLandmark.RIGHT_SHOULDER,
        PoseLandmark.RIGHT_HIP,
        PoseLandmark.RIGHT_KNEE,
        use_3d,
    )


def calculate_ankle_angle(
    landmarks: Sequence[Landmark],
    side: str = "left",
    world_landmarks: Sequence[Landmark] | None = None,
) -> float | None:
    """Ankle angle: knee -> ankle -> foot index."""
    source, use_3d = _select_landmarks(landmarks, world_landmarks)
    if side == "left":
        return _joint_angle(
            source,
            PoseLandmark.LEFT_KNEE,
            PoseLandmark.LEFT_ANKLE,
            PoseLandmark.LEFT_FOOT_INDEX,
            use_3d,
        )
    return _joint_angle(
        source,
        PoseLandmark.RIGHT_KNEE,
        PoseLandmark.RIGHT_ANKLE,
        PoseLandmark.RIGHT_FOOT_INDEX,
        use_3d,
    )


def calculate_torso_angle(
    landmarks: Sequence[Landmark],
    world_landmarks: Sequence[Landmark] | None = None,
) -> float | None:
    """
    Torso angle relative to vertical.

    Uses midpoint of shoulders and hips. Returns deviation from vertical in degrees.
    """
    source, use_3d = _select_landmarks(landmarks, world_landmarks)

    left_shoulder = _landmark(source, PoseLandmark.LEFT_SHOULDER)
    right_shoulder = _landmark(source, PoseLandmark.RIGHT_SHOULDER)
    left_hip = _landmark(source, PoseLandmark.LEFT_HIP)
    right_hip = _landmark(source, PoseLandmark.RIGHT_HIP)

    if not all((left_shoulder, right_shoulder, left_hip, right_hip)):
        return None

    shoulder_mid = Landmark(
        x=(left_shoulder.x + right_shoulder.x) / 2,  # type: ignore[union-attr]
        y=(left_shoulder.y + right_shoulder.y) / 2,  # type: ignore[union-attr]
        z=(left_shoulder.z + right_shoulder.z) / 2,  # type: ignore[union-attr]
    )
    hip_mid = Landmark(
        x=(left_hip.x + right_hip.x) / 2,  # type: ignore[union-attr]
        y=(left_hip.y + right_hip.y) / 2,  # type: ignore[union-attr]
        z=(left_hip.z + right_hip.z) / 2,  # type: ignore[union-attr]
    )

    dx = shoulder_mid.x - hip_mid.x
    dy = shoulder_mid.y - hip_mid.y
    dz = shoulder_mid.z - hip_mid.z

    if dx == 0 and dy == 0 and (not use_3d or dz == 0):
        return 0.0

    if use_3d:
        # World coords: +Y is up; vertical reference is (0, 1, 0)
        vertical = (0.0, 1.0, 0.0)
        torso = (dx, dy, dz)
        dot = vertical[0] * torso[0] + vertical[1] * torso[1] + vertical[2] * torso[2]
        mag_torso = math.sqrt(dx**2 + dy**2 + dz**2)
    else:
        # Image coords: vertical points up (negative y)
        vertical = (0.0, -1.0)
        torso = (dx, dy)
        dot = vertical[0] * torso[0] + vertical[1] * torso[1]
        mag_torso = math.hypot(dx, dy)

    if mag_torso == 0:
        return 0.0

    cos_angle = max(-1.0, min(1.0, dot / mag_torso))
    return math.degrees(math.acos(cos_angle))


def calculate_all_joint_angles(
    landmarks: Sequence[Landmark],
    world_landmarks: Sequence[Landmark] | None = None,
) -> JointAngles:
    """Compute all supported joint angles for a single frame."""
    return JointAngles(
        left_knee=calculate_knee_angle(landmarks, "left", world_landmarks),
        right_knee=calculate_knee_angle(landmarks, "right", world_landmarks),
        left_hip=calculate_hip_angle(landmarks, "left", world_landmarks),
        right_hip=calculate_hip_angle(landmarks, "right", world_landmarks),
        left_ankle=calculate_ankle_angle(landmarks, "left", world_landmarks),
        right_ankle=calculate_ankle_angle(landmarks, "right", world_landmarks),
        torso=calculate_torso_angle(landmarks, world_landmarks),
    )
