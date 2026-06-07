from dataclasses import dataclass, field
from typing import Any


@dataclass
class Landmark:
    x: float
    y: float
    z: float
    visibility: float = 1.0


@dataclass
class FrameLandmarks:
    frame_index: int
    timestamp_ms: int
    landmarks: list[Landmark]
    detected: bool = True
    # Real-world 3D coords (meters, hip-center origin) — preferred for form analysis.
    world_landmarks: list[Landmark] = field(default_factory=list)


@dataclass
class JointAngles:
    left_knee: float | None = None
    right_knee: float | None = None
    left_hip: float | None = None
    right_hip: float | None = None
    left_ankle: float | None = None
    right_ankle: float | None = None
    torso: float | None = None

    def to_dict(self) -> dict[str, float]:
        result: dict[str, float] = {}
        if self.left_knee is not None:
            result["left_knee"] = round(self.left_knee, 1)
        if self.right_knee is not None:
            result["right_knee"] = round(self.right_knee, 1)
        if self.left_hip is not None:
            result["left_hip"] = round(self.left_hip, 1)
        if self.right_hip is not None:
            result["right_hip"] = round(self.right_hip, 1)
        if self.left_ankle is not None:
            result["left_ankle"] = round(self.left_ankle, 1)
        if self.right_ankle is not None:
            result["right_ankle"] = round(self.right_ankle, 1)
        if self.torso is not None:
            result["torso"] = round(self.torso, 1)
        return result

    def summary(self) -> dict[str, float]:
        """Return representative angles for API response."""
        result: dict[str, float] = {}
        if self.left_knee is not None:
            result["left_knee"] = round(self.left_knee, 1)
        if self.right_knee is not None:
            result["right_knee"] = round(self.right_knee, 1)

        hip_values = [v for v in (self.left_hip, self.right_hip) if v is not None]
        if hip_values:
            result["hip"] = round(sum(hip_values) / len(hip_values), 1)

        return result


@dataclass
class FrameMetrics:
    frame_index: int
    timestamp_ms: int
    joint_angles: JointAngles
    flags: dict[str, bool] = field(default_factory=dict)
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass
class FormIssue:
    issue: str
    severity: str
    feedback: str
    penalty: float = 0.0

    def to_dict(self) -> dict[str, str]:
        return {
            "issue": self.issue,
            "severity": self.severity,
            "feedback": self.feedback,
        }


@dataclass
class AnalysisResult:
    exercise: str
    score: int
    issues: list[FormIssue]
    joint_angles: dict[str, float]
    frame_metrics: list[FrameMetrics] = field(default_factory=list)
    metrics_file: str | None = None

    def to_response(self) -> dict[str, Any]:
        return {
            "exercise": self.exercise,
            "score": self.score,
            "issues": [issue.to_dict() for issue in self.issues],
            "joint_angles": self.joint_angles,
        }
