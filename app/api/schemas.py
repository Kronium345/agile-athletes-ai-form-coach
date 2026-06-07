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


class ExerciseCatalogItem(BaseModel):
    id: str
    name: str
    description: str
    muscle_groups: list[str]
    filming_tip: str
    available: bool


class ExerciseCatalogResponse(BaseModel):
    exercises: list[ExerciseCatalogItem]
    coach_enabled: list[str]
    specialized: list[str]
    coach_launch: list[str]
