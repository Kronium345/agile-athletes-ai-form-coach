"""Shared test fixtures."""

import pytest

from app.exercises.registry import ExerciseRegistry


@pytest.fixture
def registry() -> ExerciseRegistry:
    return ExerciseRegistry()
