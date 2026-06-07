import logging

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile

from app.api.schemas import (
    AnalyzeFormResponse,
    ExerciseCatalogItem,
    ExerciseCatalogResponse,
    FormIssueResponse,
    HealthResponse,
    RootResponse,
)
from app.core.config import get_settings
from app.core.dependencies import get_exercise_registry, get_form_analyzer_service
from app.exercises.registry import ExerciseRegistry
from app.services.form_analyzer import FormAnalyzerService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/", response_model=RootResponse)
def root(registry: ExerciseRegistry = Depends(get_exercise_registry)) -> RootResponse:
    settings = get_settings()
    return RootResponse(
        name=settings.app_name,
        version=settings.app_version,
        description="AI Form Coach API — upload exercise videos for pose analysis and form scoring.",
        endpoints={
            "health": "/health",
            "exercises": "/exercises",
            "analyze_form": "POST /analyze-form",
            "docs": "/docs",
            "openapi": "/openapi.json",
        },
    )


@router.get("/exercises", response_model=ExerciseCatalogResponse)
def list_exercises(registry: ExerciseRegistry = Depends(get_exercise_registry)) -> ExerciseCatalogResponse:
    """
    Return the full exercise catalog.

    Edit app/data/exercises.json to add exercises to the app UI.
    Set available=true and implement an analyzer to enable form scoring.
    """
    catalog = registry.catalog
    return ExerciseCatalogResponse(
        exercises=[ExerciseCatalogItem(**e.to_dict()) for e in catalog.list_all()],
        coach_enabled=registry.list_exercises(),
        specialized=registry.list_specialized(),
        coach_launch=registry.list_coach_launch(),
    )


@router.get("/health", response_model=HealthResponse)
def health_check(registry: ExerciseRegistry = Depends(get_exercise_registry)) -> HealthResponse:
    settings = get_settings()
    return HealthResponse(
        status="ok",
        version=settings.app_version,
        exercises=registry.list_exercises(),
    )


@router.post("/analyze-form", response_model=AnalyzeFormResponse)
async def analyze_form(
    video: UploadFile = File(..., description="Exercise video (.mp4)"),
    exercise: str = Form(default="squat", description="Exercise type to analyze"),
    service: FormAnalyzerService = Depends(get_form_analyzer_service),
    registry: ExerciseRegistry = Depends(get_exercise_registry),
) -> AnalyzeFormResponse:
    """
    Analyze exercise form from an uploaded video.

    Accepts MP4 video and returns form score, issues, and joint angles.
    """
    if not video.filename:
        raise HTTPException(status_code=400, detail="No filename provided")

    suffix = video.filename.lower()
    if not suffix.endswith((".mp4", ".mov", ".avi", ".mkv")):
        raise HTTPException(
            status_code=400,
            detail="Unsupported video format. Upload .mp4, .mov, .avi, or .mkv",
        )

    try:
        registry.get(exercise)
    except KeyError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    content = await video.read()
    if not content:
        raise HTTPException(status_code=400, detail="Empty video file")

    settings = get_settings()
    max_bytes = settings.max_video_size_mb * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"Video exceeds maximum size of {settings.max_video_size_mb} MB",
        )

    try:
        result = service.analyze_video(
            video_bytes=content,
            exercise=exercise,
            filename=video.filename,
        )
    except FileNotFoundError as exc:
        logger.error("Model not found: %s", exc)
        raise HTTPException(
            status_code=503,
            detail="Pose detection model not available. Contact administrator.",
        ) from exc
    except OSError as exc:
        logger.error("MediaPipe failed to load: %s", exc)
        raise HTTPException(
            status_code=503,
            detail="Pose detection engine unavailable. Server may need redeploying.",
        ) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        logger.exception("Analysis failed")
        raise HTTPException(status_code=500, detail="Form analysis failed") from exc

    return AnalyzeFormResponse(
        exercise=result.exercise,
        score=result.score,
        issues=[FormIssueResponse(**issue.to_dict()) for issue in result.issues],
        joint_angles=result.joint_angles,
    )
