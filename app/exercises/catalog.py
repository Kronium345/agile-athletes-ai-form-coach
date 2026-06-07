"""Exercise catalog — loaded from app/data/exercises.json."""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

CATALOG_PATH = Path(__file__).resolve().parent.parent / "data" / "exercises.json"

# Legacy alias for backward-compatible API requests
EXERCISE_ALIASES: dict[str, str] = {
    "squat": "back_squat",
}


@dataclass(frozen=True)
class ExerciseDefinition:
    id: str
    name: str
    description: str
    muscle_groups: list[str]
    filming_tip: str
    available: bool

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "muscle_groups": self.muscle_groups,
            "filming_tip": self.filming_tip,
            "available": self.available,
        }


class ExerciseCatalog:
    """
    Exercise catalog for Agile Athletes.

    Edit app/data/exercises.json to add exercises.
    Set available=true for exercises enabled in the AI Form Coach flow.
    """

    def __init__(self, catalog_path: Path = CATALOG_PATH) -> None:
        self._exercises: dict[str, ExerciseDefinition] = {}
        self._load(catalog_path)

    def _load(self, path: Path) -> None:
        if not path.exists():
            raise FileNotFoundError(f"Exercise catalog not found: {path}")

        data = json.loads(path.read_text(encoding="utf-8"))
        for item in data.get("exercises", []):
            exercise = ExerciseDefinition(
                id=item["id"],
                name=item["name"],
                description=item["description"],
                muscle_groups=item.get("muscle_groups", []),
                filming_tip=item.get("filming_tip", ""),
                available=bool(item.get("available", False)),
            )
            self._exercises[exercise.id] = exercise

    @staticmethod
    def normalize_id(exercise_id: str) -> str:
        key = exercise_id.lower().strip().replace(" ", "_").replace("-", "_")
        return EXERCISE_ALIASES.get(key, key)

    def get(self, exercise_id: str) -> ExerciseDefinition | None:
        return self._exercises.get(self.normalize_id(exercise_id))

    def list_all(self) -> list[ExerciseDefinition]:
        return sorted(self._exercises.values(), key=lambda e: e.name.lower())

    def list_available(self) -> list[ExerciseDefinition]:
        return [e for e in self.list_all() if e.available]

    def list_available_ids(self) -> list[str]:
        return sorted(e.id for e in self.list_available())


@lru_cache
def get_exercise_catalog() -> ExerciseCatalog:
    return ExerciseCatalog()
