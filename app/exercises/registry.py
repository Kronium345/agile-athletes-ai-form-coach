"""Exercise analyzer registry for extensible exercise support."""

from app.exercises.base import ExerciseAnalyzer
from app.exercises.catalog import ExerciseCatalog, get_exercise_catalog
from app.exercises.deadlift import DeadliftAnalyzer
from app.exercises.generic import GenericAnalyzer
from app.exercises.squat import SquatAnalyzer

# Detailed squat form rules (depth, knee valgus, forward lean, heel lift)
SQUAT_EXERCISE_IDS = frozenset(
    {
        "back_squat",
        "front_squat",
        "goblet_squat",
        "box_squat",
        "pause_squat",
        "overhead_squat",
        "zercher_squat",
        "safety_bar_squat",
        "hack_squat",
        "bodyweight_squat",
    }
)

# Detailed hip-hinge form rules (rounded back, lockout, bar path)
DEADLIFT_EXERCISE_IDS = frozenset(
    {
        "deadlift",
        "conventional_deadlift",
        "sumo_deadlift",
        "romanian_deadlift",
        "stiff_leg_deadlift",
        "trap_bar_deadlift",
        "single_leg_romanian_deadlift",
    }
)


class ExerciseRegistry:
    """
    Routes catalog exercises to the correct analyzer.

    - Squat variants → SquatAnalyzer (specialized)
    - Deadlift/hinge variants → DeadliftAnalyzer (specialized)
    - Other available exercises → GenericAnalyzer (pose quality + ROM)
    """

    def __init__(self, catalog: ExerciseCatalog | None = None) -> None:
        self._catalog = catalog or get_exercise_catalog()

    def get(self, exercise: str) -> ExerciseAnalyzer:
        key = self._catalog.normalize_id(exercise)
        catalog_entry = self._catalog.get(key)

        if not catalog_entry:
            sample = ", ".join(e.id for e in self._catalog.list_available()[:8])
            raise KeyError(
                f"Exercise '{exercise}' is not in the catalog. "
                f"See GET /exercises for valid IDs (e.g. {sample})."
            )

        if not catalog_entry.available:
            raise KeyError(
                f"Exercise '{catalog_entry.name}' is in the library but not enabled "
                "for AI Form Coach yet."
            )

        if key in SQUAT_EXERCISE_IDS:
            return SquatAnalyzer(key)
        if key in DEADLIFT_EXERCISE_IDS:
            return DeadliftAnalyzer(key)
        return GenericAnalyzer(key)

    def list_exercises(self) -> list[str]:
        """Exercise IDs enabled for AI Form Coach analysis."""
        return self._catalog.list_available_ids()

    def list_specialized(self) -> list[str]:
        """Available exercises with dedicated form rules."""
        return sorted(
            eid for eid in self.list_exercises() if eid in SQUAT_EXERCISE_IDS | DEADLIFT_EXERCISE_IDS
        )

    def list_coach_launch(self) -> list[str]:
        """Core MVP exercises shown on the primary AI Form Coach screen."""
        launch = [
            "back_squat",
            "front_squat",
            "deadlift",
            "romanian_deadlift",
            "bench_press",
            "overhead_press",
            "pull_up",
        ]
        available = set(self.list_exercises())
        return [eid for eid in launch if eid in available]

    @property
    def catalog(self) -> ExerciseCatalog:
        return self._catalog
