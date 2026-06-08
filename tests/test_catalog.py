from app.exercises.catalog import ExerciseCatalog
from app.exercises.registry import ExerciseRegistry


class TestExerciseCatalog:
    def test_loads_large_catalog(self) -> None:
        catalog = ExerciseCatalog()
        assert len(catalog.list_all()) >= 120

    def test_coach_enabled_count(self) -> None:
        catalog = ExerciseCatalog()
        enabled = catalog.list_available()
        assert 45 <= len(enabled) <= 55
        assert any(e.id == "back_squat" for e in enabled)
        assert any(e.id == "incline_bench_press" for e in enabled)

    def test_library_exercises_locked(self) -> None:
        catalog = ExerciseCatalog()
        pec = catalog.get("pec_deck")
        assert pec is not None
        assert pec.available is False

    def test_back_squat_alias(self) -> None:
        catalog = ExerciseCatalog()
        assert catalog.normalize_id("squat") == "back_squat"
        assert catalog.get("squat") is not None


class TestExerciseRegistry:
    def test_resolves_specialized_squat(self) -> None:
        registry = ExerciseRegistry()
        assert registry.get("back_squat").name == "back_squat"
        assert registry.get("squat").name == "back_squat"
        assert registry.get("goblet_squat").name == "goblet_squat"

    def test_resolves_specialized_deadlift(self) -> None:
        registry = ExerciseRegistry()
        assert registry.get("romanian_deadlift").name == "romanian_deadlift"
        assert registry.get("trap_bar_deadlift").name == "trap_bar_deadlift"

    def test_falls_back_to_generic(self) -> None:
        registry = ExerciseRegistry()
        assert registry.get("bench_press").name == "bench_press"
        assert registry.get("plank").name == "plank"

    def test_rejects_library_only_exercise(self) -> None:
        registry = ExerciseRegistry()
        try:
            registry.get("pec_deck")
            assert False, "expected KeyError"
        except KeyError as exc:
            assert "not enabled" in str(exc)

    def test_coach_launch_matches_enabled(self) -> None:
        registry = ExerciseRegistry()
        assert registry.list_coach_launch() == registry.list_exercises()

    def test_specialized_includes_squat_and_hinge(self) -> None:
        registry = ExerciseRegistry()
        specialized = registry.list_specialized()
        assert "back_squat" in specialized
        assert "romanian_deadlift" in specialized
        assert "bench_press" not in specialized
