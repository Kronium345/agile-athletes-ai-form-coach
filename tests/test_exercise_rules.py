import pytest

from app.domain.models import FormIssue, FrameMetrics, JointAngles, Landmark
from app.utils import exercise_rules
from app.utils.landmarks import PoseLandmark


def _lm(x: float, y: float) -> Landmark:
    return Landmark(x=x, y=y, z=0.0, visibility=1.0)


def _squat_landmarks(
    hip_y: float = 0.55,
    knee_y: float = 0.5,
    knee_x_offset: float = 0.0,
    heel_lift: bool = False,
) -> list[Landmark]:
    """Build synthetic landmarks for squat testing."""
    landmarks = [_lm(0.5, 0.5)] * 33

    # Shoulders
    landmarks[PoseLandmark.LEFT_SHOULDER] = _lm(0.4, 0.2)
    landmarks[PoseLandmark.RIGHT_SHOULDER] = _lm(0.6, 0.2)

    # Hips
    landmarks[PoseLandmark.LEFT_HIP] = _lm(0.4, hip_y)
    landmarks[PoseLandmark.RIGHT_HIP] = _lm(0.6, hip_y)

    # Knees (with optional valgus offset)
    landmarks[PoseLandmark.LEFT_KNEE] = _lm(0.4 + knee_x_offset, knee_y)
    landmarks[PoseLandmark.RIGHT_KNEE] = _lm(0.6 - knee_x_offset, knee_y)

    # Ankles
    landmarks[PoseLandmark.LEFT_ANKLE] = _lm(0.4, 0.75)
    landmarks[PoseLandmark.RIGHT_ANKLE] = _lm(0.6, 0.75)

    # Heels
    heel_y = 0.73 if heel_lift else 0.76
    landmarks[PoseLandmark.LEFT_HEEL] = _lm(0.4, heel_y)
    landmarks[PoseLandmark.RIGHT_HEEL] = _lm(0.6, heel_y)

    # Feet
    landmarks[PoseLandmark.LEFT_FOOT_INDEX] = _lm(0.4, 0.78)
    landmarks[PoseLandmark.RIGHT_FOOT_INDEX] = _lm(0.6, 0.78)

    return landmarks


class TestDepthCheck:
    def test_good_depth_when_hip_below_knee(self) -> None:
        landmarks = _squat_landmarks(hip_y=0.55, knee_y=0.5)
        ok, _ = exercise_rules.check_depth(landmarks)
        assert ok is True

    def test_insufficient_depth_when_hip_above_knee(self) -> None:
        landmarks = _squat_landmarks(hip_y=0.45, knee_y=0.5)
        ok, _ = exercise_rules.check_depth(landmarks)
        assert ok is False


class TestKneeValgus:
    def test_no_valgus_with_aligned_knees(self) -> None:
        landmarks = _squat_landmarks(knee_x_offset=0.0)
        valgus, _ = exercise_rules.check_knee_valgus(landmarks, "left")
        assert valgus is False

    def test_valgus_when_knee_collapses_inward(self) -> None:
        landmarks = _squat_landmarks(knee_x_offset=-0.08)
        valgus, _ = exercise_rules.check_knee_valgus(landmarks, "left")
        assert valgus is True


class TestForwardLean:
    def test_no_excessive_lean_at_small_angle(self) -> None:
        excessive, _ = exercise_rules.check_forward_lean(30.0)
        assert excessive is False

    def test_excessive_lean_at_large_angle(self) -> None:
        excessive, _ = exercise_rules.check_forward_lean(50.0)
        assert excessive is True


class TestHeelLift:
    def test_no_heel_lift_when_planted(self) -> None:
        landmarks = _squat_landmarks(heel_lift=False)
        lifted, _ = exercise_rules.check_heel_lift(landmarks, "left")
        assert lifted is False

    def test_heel_lift_detected(self) -> None:
        landmarks = _squat_landmarks(heel_lift=True)
        lifted, _ = exercise_rules.check_heel_lift(landmarks, "left")
        assert lifted is True


class TestDepthCheckWorld:
    def test_good_depth_in_world_coords(self) -> None:
        world = [_lm(0, 0)] * 33
        world[PoseLandmark.LEFT_HIP] = Landmark(x=0, y=0.4, z=0, visibility=1.0)
        world[PoseLandmark.RIGHT_HIP] = Landmark(x=0, y=0.4, z=0, visibility=1.0)
        world[PoseLandmark.LEFT_KNEE] = Landmark(x=0, y=0.5, z=0, visibility=1.0)
        world[PoseLandmark.RIGHT_KNEE] = Landmark(x=0, y=0.5, z=0, visibility=1.0)

        ok, meta = exercise_rules.check_depth([], world_landmarks=world)
        assert ok is True
        assert meta["coordinate_space"] == "world"

    def test_insufficient_depth_in_world_coords(self) -> None:
        world = [_lm(0, 0)] * 33
        world[PoseLandmark.LEFT_HIP] = Landmark(x=0, y=0.6, z=0, visibility=1.0)
        world[PoseLandmark.RIGHT_HIP] = Landmark(x=0, y=0.6, z=0, visibility=1.0)
        world[PoseLandmark.LEFT_KNEE] = Landmark(x=0, y=0.5, z=0, visibility=1.0)
        world[PoseLandmark.RIGHT_KNEE] = Landmark(x=0, y=0.5, z=0, visibility=1.0)

        ok, _ = exercise_rules.check_depth([], world_landmarks=world)
        assert ok is False


class TestScoring:
    def test_perfect_score_with_no_issues(self) -> None:
        score = exercise_rules.calculate_form_score([])
        assert score == 100

    def test_score_decreases_with_penalties(self) -> None:
        issues = [
            FormIssue(
                issue="Test",
                severity="medium",
                feedback="Test",
                penalty=18.0,
            )
        ]
        score = exercise_rules.calculate_form_score(issues)
        assert score == 82

    def test_score_clamped_to_zero(self) -> None:
        issues = [
            FormIssue(issue="A", severity="high", feedback="A", penalty=60.0),
            FormIssue(issue="B", severity="high", feedback="B", penalty=60.0),
        ]
        assert exercise_rules.calculate_form_score(issues) == 0


class TestAggregateIssues:
    def test_detects_knee_valgus_across_frames(self) -> None:
        frame_metrics = []
        for _ in range(10):
            landmarks = _squat_landmarks(knee_x_offset=-0.08)
            fm = FrameMetrics(
                frame_index=0,
                timestamp_ms=0,
                joint_angles=JointAngles(torso=20.0),
            )
            exercise_rules.evaluate_frame(fm, landmarks)
            frame_metrics.append(fm)

        issues = exercise_rules.aggregate_issues(frame_metrics)
        issue_names = [i.issue for i in issues]
        assert "Knees collapsing inward" in issue_names

    def test_no_pose_returns_high_severity_issue(self) -> None:
        issues = exercise_rules.aggregate_issues([])
        assert len(issues) == 1
        assert issues[0].severity == "high"
