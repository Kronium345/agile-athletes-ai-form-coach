"""Shared form scoring utilities."""

from app.domain.models import FormIssue


def calculate_form_score(issues: list[FormIssue]) -> int:
    """Start at 100 and subtract weighted penalties."""
    score = 100.0
    for issue in issues:
        score -= issue.penalty
    return max(0, min(100, int(round(score))))
