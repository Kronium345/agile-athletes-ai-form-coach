import math

import pytest

from app.domain.models import Landmark
from app.utils.angle_calculator import (
    calculate_all_joint_angles,
    calculate_angle,
    calculate_ankle_angle,
    calculate_hip_angle,
    calculate_knee_angle,
    calculate_torso_angle,
)
from app.utils.landmarks import PoseLandmark


def _lm(x: float, y: float, z: float = 0.0) -> Landmark:
    return Landmark(x=x, y=y, z=z, visibility=1.0)


class TestCalculateAngle:
    def test_right_angle(self) -> None:
        a = _lm(0, 0)
        b = _lm(0, 1)
        c = _lm(1, 1)
        assert calculate_angle(a, b, c) == pytest.approx(90.0, abs=0.1)

    def test_straight_line(self) -> None:
        a = _lm(0, 0)
        b = _lm(0, 1)
        c = _lm(0, 2)
        assert calculate_angle(a, b, c) == pytest.approx(180.0, abs=0.1)

    def test_zero_magnitude_returns_zero(self) -> None:
        b = _lm(0, 0)
        assert calculate_angle(b, b, _lm(1, 0)) == 0.0


class TestKneeAngle:
    def test_calculates_knee_angle(self) -> None:
        landmarks = [_lm(0, 0)] * 33
        landmarks[PoseLandmark.LEFT_HIP] = _lm(0.5, 0.3)
        landmarks[PoseLandmark.LEFT_KNEE] = _lm(0.5, 0.5)
        landmarks[PoseLandmark.LEFT_ANKLE] = _lm(0.5, 0.7)

        angle = calculate_knee_angle(landmarks, "left")
        assert angle is not None
        assert angle == pytest.approx(180.0, abs=1.0)

    def test_returns_none_when_landmarks_missing(self) -> None:
        landmarks = [Landmark(x=0, y=0, z=0, visibility=0.0)] * 33
        assert calculate_knee_angle(landmarks, "left") is None


class TestHipAngle:
    def test_calculates_hip_angle(self) -> None:
        landmarks = [_lm(0, 0)] * 33
        landmarks[PoseLandmark.LEFT_SHOULDER] = _lm(0.4, 0.1)
        landmarks[PoseLandmark.LEFT_HIP] = _lm(0.5, 0.3)
        landmarks[PoseLandmark.LEFT_KNEE] = _lm(0.5, 0.5)

        angle = calculate_hip_angle(landmarks, "left")
        assert angle is not None
        assert 0 < angle <= 180


class TestAnkleAngle:
    def test_calculates_ankle_angle(self) -> None:
        landmarks = [_lm(0, 0)] * 33
        landmarks[PoseLandmark.LEFT_KNEE] = _lm(0.5, 0.5)
        landmarks[PoseLandmark.LEFT_ANKLE] = _lm(0.5, 0.7)
        landmarks[PoseLandmark.LEFT_FOOT_INDEX] = _lm(0.5, 0.75)

        angle = calculate_ankle_angle(landmarks, "left")
        assert angle is not None
        assert angle == pytest.approx(180.0, abs=1.0)


class TestTorsoAngle:
    def test_vertical_torso_is_zero(self) -> None:
        landmarks = [_lm(0, 0)] * 33
        landmarks[PoseLandmark.LEFT_SHOULDER] = _lm(0.4, 0.2)
        landmarks[PoseLandmark.RIGHT_SHOULDER] = _lm(0.6, 0.2)
        landmarks[PoseLandmark.LEFT_HIP] = _lm(0.4, 0.5)
        landmarks[PoseLandmark.RIGHT_HIP] = _lm(0.6, 0.5)

        angle = calculate_torso_angle(landmarks)
        assert angle is not None
        assert angle == pytest.approx(0.0, abs=1.0)

    def test_forward_lean_detected(self) -> None:
        landmarks = [_lm(0, 0)] * 33
        landmarks[PoseLandmark.LEFT_SHOULDER] = _lm(0.6, 0.3)
        landmarks[PoseLandmark.RIGHT_SHOULDER] = _lm(0.7, 0.3)
        landmarks[PoseLandmark.LEFT_HIP] = _lm(0.4, 0.5)
        landmarks[PoseLandmark.RIGHT_HIP] = _lm(0.5, 0.5)

        angle = calculate_torso_angle(landmarks)
        assert angle is not None
        assert angle > 20


class TestCalculateAngle3D:
    def test_right_angle_in_3d(self) -> None:
        a = _lm(1, 0, 0)
        b = _lm(0, 0, 0)
        c = _lm(0, 1, 0)
        from app.utils.angle_calculator import calculate_angle_3d

        assert calculate_angle_3d(a, b, c) == pytest.approx(90.0, abs=0.1)


class TestWorldLandmarkPreference:
    def test_uses_world_landmarks_when_provided(self) -> None:
        image = [_lm(0.5, 0.5)] * 33
        world = [_lm(0, 0, 0)] * 33
        world[PoseLandmark.LEFT_HIP] = _lm(0, 0.5, 0)
        world[PoseLandmark.LEFT_KNEE] = _lm(0, 0, 0)
        world[PoseLandmark.LEFT_ANKLE] = _lm(0, -0.5, 0)

        angle = calculate_knee_angle(image, "left", world_landmarks=world)
        assert angle is not None
        assert angle == pytest.approx(180.0, abs=1.0)


class TestCalculateAllJointAngles:
    def test_returns_joint_angles_object(self) -> None:
        landmarks = [_lm(0.5, 0.5)] * 33
        angles = calculate_all_joint_angles(landmarks)
        assert angles.left_knee is not None
        assert angles.right_knee is not None
