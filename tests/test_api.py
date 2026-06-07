from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from app.core.dependencies import get_exercise_registry, get_form_analyzer_service
from app.domain.models import AnalysisResult, FormIssue
from app.exercises.registry import ExerciseRegistry
from app.main import create_app


@pytest.fixture
def mock_analyzer_service() -> MagicMock:
    service = MagicMock()
    service.analyze_video.return_value = AnalysisResult(
        exercise="squat",
        score=82,
        issues=[
            FormIssue(
                issue="Knees collapsing inward",
                severity="medium",
                feedback="Push knees outward during descent.",
                penalty=18.0,
            )
        ],
        joint_angles={"left_knee": 92.0, "right_knee": 88.0, "hip": 76.0},
    )
    return service


@pytest.fixture
def client(mock_analyzer_service: MagicMock) -> TestClient:
    app = create_app()
    app.dependency_overrides[get_form_analyzer_service] = lambda: mock_analyzer_service
    app.dependency_overrides[get_exercise_registry] = lambda: ExerciseRegistry()
    yield TestClient(app)
    app.dependency_overrides.clear()


class TestRootEndpoint:
    def test_root_returns_api_info(self, client: TestClient) -> None:
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Agile Athletes AI Form Coach"
        assert data["version"] == "0.1.0"
        assert data["endpoints"]["health"] == "/health"
        assert data["endpoints"]["docs"] == "/docs"
        assert "POST /analyze-form" in data["endpoints"]["analyze_form"]


class TestHealthEndpoint:
    def test_health_returns_ok(self, client: TestClient) -> None:
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert "back_squat" in data["exercises"]
        assert "deadlift" in data["exercises"]


class TestExercisesEndpoint:
    def test_exercises_returns_catalog(self, client: TestClient) -> None:
        response = client.get("/exercises")
        assert response.status_code == 200
        data = response.json()
        assert len(data["exercises"]) >= 120
        assert "back_squat" in data["coach_enabled"]
        assert "back_squat" in data["specialized"]
        bench = next(e for e in data["exercises"] if e["id"] == "bench_press")
        assert bench["available"] is True
        pec = next(e for e in data["exercises"] if e["id"] == "pec_deck")
        assert pec["available"] is False


class TestAnalyzeFormEndpoint:
    def test_analyze_form_success(self, client: TestClient, mock_analyzer_service: MagicMock) -> None:
        response = client.post(
            "/analyze-form",
            files={"video": ("squat.mp4", b"fake-video-content", "video/mp4")},
            data={"exercise": "squat"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["exercise"] == "squat"
        assert data["score"] == 82
        assert len(data["issues"]) == 1
        assert data["issues"][0]["issue"] == "Knees collapsing inward"
        assert data["joint_angles"]["left_knee"] == 92.0
        mock_analyzer_service.analyze_video.assert_called_once()

    def test_rejects_unknown_exercise(self, client: TestClient) -> None:
        response = client.post(
            "/analyze-form",
            files={"video": ("squat.mp4", b"content", "video/mp4")},
            data={"exercise": "unknown_lift"},
        )
        assert response.status_code == 400
        assert "not in the catalog" in response.json()["detail"]

    def test_rejects_empty_video(self, client: TestClient) -> None:
        response = client.post(
            "/analyze-form",
            files={"video": ("squat.mp4", b"", "video/mp4")},
        )
        assert response.status_code == 400

    def test_rejects_invalid_format(self, client: TestClient) -> None:
        response = client.post(
            "/analyze-form",
            files={"video": ("squat.gif", b"content", "image/gif")},
        )
        assert response.status_code == 400
