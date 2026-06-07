from app.exercises.catalog import ExerciseCatalog
from app.exercises.registry import ExerciseRegistry


class TestExerciseCatalog:
    def test_loads_large_catalog(self) -> None:
        catalog = ExerciseCatalog()
        assert len(catalog.list_all()) >= 120

    def test_coach_enabled_subset(self) -> None:
        catalog = ExerciseCatalog()
        enabled = catalog.list_available()
        assert 15 <= len(enabled) <= 30
        assert any(e.id == "back_squat" for e in enabled)

    def test_back_squat_alias(self) -> None:
        catalog = ExerciseCatalog()
        assert catalog.normalize_id("squat") == "back_squat"
        assert catalog.get("squat") is not None

    def test_get_by_id(self) -> None:
        catalog = ExerciseCatalog()
        bench = catalog.get("bench_press")
        assert bench is not None
        assert bench.available is True


class TestExerciseRegistry:
    def test_resolves_specialized_squat(self) -> None:
        registry = ExerciseRegistry()
        assert registry.get("back_squat").name == "back_squat"
        assert registry.get("squat").name == "back_squat"

    def test_resolves_specialized_deadlift(self) -> None:
        registry = ExerciseRegistry()
        assert registry.get("romanian_deadlift").name == "romanian_deadlift"

    def test_falls_back_to_generic(self) -> None:
        registry = ExerciseRegistry()
        assert registry.get("bench_press").name == "bench_press"

    def test_rejects_library_only_exercise(self) -> None:
        registry = ExerciseRegistry()
        try:
            registry.get("pec_deck")
            assert False, "expected KeyError"
        except KeyError as exc:
            assert "not enabled" in str(exc)

    def test_coach_launch_list(self) -> None:
        registry = ExerciseRegistry()
        launch = registry.list_coach_launch()
        assert "back_squat" in launch
        assert "pull_up" in launch

    def test_specialized_includes_squat_variants(self) -> None:
        registry = ExerciseRegistry()
        specialized = registry.list_specialized()
        assert "back_squat" in specialized
        assert "romanian_deadlift" in specialized
