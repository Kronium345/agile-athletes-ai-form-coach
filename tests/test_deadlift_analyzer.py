from app.domain.models import FrameLandmarks, Landmark
from app.exercises.deadlift import DeadliftAnalyzer
from app.utils.landmarks import PoseLandmark


def _lm(x: float, y: float) -> Landmark:
    return Landmark(x=x, y=y, z=0.0, visibility=1.0)


def _make_deadlift_frame(
    shoulder_x: float = 0.45,
    hip_y: float = 0.45,
    torso_angle_frame: bool = False,
) -> FrameLandmarks:
    """Synthetic side-view deadlift pose."""
    landmarks = [_lm(0.5, 0.5)] * 33
    landmarks[PoseLandmark.LEFT_SHOULDER] = _lm(shoulder_x, 0.25)
    landmarks[PoseLandmark.RIGHT_SHOULDER] = _lm(shoulder_x + 0.05, 0.25)
    landmarks[PoseLandmark.LEFT_HIP] = _lm(0.42, hip_y)
    landmarks[PoseLandmark.RIGHT_HIP] = _lm(0.52, hip_y)
    landmarks[PoseLandmark.LEFT_KNEE] = _lm(0.42, 0.58)
    landmarks[PoseLandmark.RIGHT_KNEE] = _lm(0.52, 0.58)
    landmarks[PoseLandmark.LEFT_ANKLE] = _lm(0.42, 0.75)
    landmarks[PoseLandmark.RIGHT_ANKLE] = _lm(0.52, 0.75)
    landmarks[PoseLandmark.LEFT_HEEL] = _lm(0.42, 0.76)
    landmarks[PoseLandmark.RIGHT_HEEL] = _lm(0.52, 0.76)
    landmarks[PoseLandmark.LEFT_FOOT_INDEX] = _lm(0.42, 0.78)
    landmarks[PoseLandmark.RIGHT_FOOT_INDEX] = _lm(0.52, 0.78)

    if torso_angle_frame:
        landmarks[PoseLandmark.LEFT_SHOULDER] = _lm(0.55, 0.35)
        landmarks[PoseLandmark.RIGHT_SHOULDER] = _lm(0.60, 0.35)

    return FrameLandmarks(
        frame_index=0,
        timestamp_ms=0,
        landmarks=landmarks,
        detected=True,
    )


class TestDeadliftAnalyzer:
    def test_analyzer_name(self) -> None:
        assert DeadliftAnalyzer().name == "deadlift"

    def test_analyze_returns_result(self) -> None:
        frames = [_make_deadlift_frame() for _ in range(5)]
        result = DeadliftAnalyzer().analyze(frames)
        assert result.exercise == "deadlift"
        assert 0 <= result.score <= 100

    def test_detects_shoulders_forward(self) -> None:
        frames = [_make_deadlift_frame(shoulder_x=0.58) for _ in range(10)]
        result = DeadliftAnalyzer().analyze(frames)
        issue_names = [i.issue for i in result.issues]
        assert "Shoulders drifting forward" in issue_names
