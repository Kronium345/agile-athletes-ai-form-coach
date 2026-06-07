from app.domain.models import FrameLandmarks, Landmark
from app.exercises.squat import SquatAnalyzer
from app.utils.landmarks import PoseLandmark


def _lm(x: float, y: float) -> Landmark:
    return Landmark(x=x, y=y, z=0.0, visibility=1.0)


def _make_squat_frame(hip_y: float = 0.55, knee_x_offset: float = 0.0) -> FrameLandmarks:
    landmarks = [_lm(0.5, 0.5)] * 33
    landmarks[PoseLandmark.LEFT_SHOULDER] = _lm(0.4, 0.2)
    landmarks[PoseLandmark.RIGHT_SHOULDER] = _lm(0.6, 0.2)
    landmarks[PoseLandmark.LEFT_HIP] = _lm(0.4, hip_y)
    landmarks[PoseLandmark.RIGHT_HIP] = _lm(0.6, hip_y)
    landmarks[PoseLandmark.LEFT_KNEE] = _lm(0.4 + knee_x_offset, 0.5)
    landmarks[PoseLandmark.RIGHT_KNEE] = _lm(0.6 - knee_x_offset, 0.5)
    landmarks[PoseLandmark.LEFT_ANKLE] = _lm(0.4, 0.75)
    landmarks[PoseLandmark.RIGHT_ANKLE] = _lm(0.6, 0.75)
    landmarks[PoseLandmark.LEFT_HEEL] = _lm(0.4, 0.76)
    landmarks[PoseLandmark.RIGHT_HEEL] = _lm(0.6, 0.76)
    landmarks[PoseLandmark.LEFT_FOOT_INDEX] = _lm(0.4, 0.78)
    landmarks[PoseLandmark.RIGHT_FOOT_INDEX] = _lm(0.6, 0.78)

    return FrameLandmarks(
        frame_index=0,
        timestamp_ms=0,
        landmarks=landmarks,
        detected=True,
    )


class TestSquatAnalyzer:
    def test_analyzer_name(self) -> None:
        assert SquatAnalyzer().name == "squat"

    def test_analyze_returns_result_structure(self) -> None:
        frames = [_make_squat_frame() for _ in range(5)]
        result = SquatAnalyzer().analyze(frames)

        assert result.exercise == "squat"
        assert 0 <= result.score <= 100
        assert isinstance(result.joint_angles, dict)
        assert len(result.frame_metrics) == 5

    def test_analyze_detects_valgus(self) -> None:
        frames = [_make_squat_frame(knee_x_offset=-0.08) for _ in range(10)]
        result = SquatAnalyzer().analyze(frames)

        issue_names = [i.issue for i in result.issues]
        assert "Knees collapsing inward" in issue_names
        assert result.score < 100

    def test_joint_angles_include_knees_and_hip(self) -> None:
        frames = [_make_squat_frame() for _ in range(3)]
        result = SquatAnalyzer().analyze(frames)

        assert "left_knee" in result.joint_angles
        assert "right_knee" in result.joint_angles
        assert "hip" in result.joint_angles
