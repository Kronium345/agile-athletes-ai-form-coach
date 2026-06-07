from functools import lru_cache

from app.core.config import get_settings
from app.exercises.registry import ExerciseRegistry
from app.services.form_analyzer import FormAnalyzerService
from app.utils.pose_detector import PoseDetector


@lru_cache
def get_pose_detector() -> PoseDetector:
    settings = get_settings()
    return PoseDetector(settings)


@lru_cache
def get_exercise_registry() -> ExerciseRegistry:
    return ExerciseRegistry()


@lru_cache
def get_form_analyzer_service() -> FormAnalyzerService:
    settings = get_settings()
    pose_detector = get_pose_detector()
    registry = get_exercise_registry()
    return FormAnalyzerService(settings, pose_detector, registry)
