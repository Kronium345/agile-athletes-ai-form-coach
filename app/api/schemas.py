from pydantic import BaseModel, Field


class RootResponse(BaseModel):
    name: str
    version: str
    description: str
    endpoints: dict[str, str]


class FormIssueResponse(BaseModel):
    issue: str
    severity: str
    feedback: str


class AnalyzeFormResponse(BaseModel):
    exercise: str
    score: int = Field(ge=0, le=100)
    issues: list[FormIssueResponse]
    joint_angles: dict[str, float]


class HealthResponse(BaseModel):
    status: str
    version: str
    exercises: list[str]
