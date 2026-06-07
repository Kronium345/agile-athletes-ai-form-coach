"""Exercise analyzer registry for extensible exercise support."""

from app.exercises.base import ExerciseAnalyzer
from app.exercises.squat import SquatAnalyzer


class ExerciseRegistry:
    """
    Registry of available exercise analyzers.

    Future exercises (deadlift, bench press, overhead press, pull-up) register here
    without modifying core pose detection logic.
    """

    def __init__(self) -> None:
        self._analyzers: dict[str, ExerciseAnalyzer] = {}
        self._register_defaults()

    def _register_defaults(self) -> None:
        self.register(SquatAnalyzer())

    def register(self, analyzer: ExerciseAnalyzer) -> None:
        self._analyzers[analyzer.name] = analyzer

    def get(self, exercise: str) -> ExerciseAnalyzer:
        key = exercise.lower().strip()
        if key not in self._analyzers:
            available = ", ".join(sorted(self._analyzers.keys()))
            raise KeyError(
                f"Exercise '{exercise}' not supported. Available: {available}"
            )
        return self._analyzers[key]

    def list_exercises(self) -> list[str]:
        return sorted(self._analyzers.keys())
