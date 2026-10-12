import pytest
from pydantic import ValidationError

from app.models import ScenarioRequest


@pytest.mark.parametrize("year", [0, 3000])
def test_request_accepts_inclusive_year_boundaries(year):
    request = ScenarioRequest(
        question=" ¿Y si...? ", year=year, unrealismLevel="realista"
    )

    assert request.question == "¿Y si...?"
    assert request.year == year


def test_request_accepts_question_at_maximum_length():
    request = ScenarioRequest(
        question="a" * 280, year=2026, unrealismLevel="ilusionante"
    )

    assert len(request.question) == 280


@pytest.mark.parametrize("question", ["", "   ", "a" * 281])
def test_request_rejects_empty_or_overlong_question(question):
    with pytest.raises(ValidationError):
        ScenarioRequest(question=question, year=2026, unrealismLevel="realista")


@pytest.mark.parametrize("year", [-1, 3001, 2026.0, "2026", True])
def test_request_rejects_out_of_range_or_non_strict_year(year):
    with pytest.raises(ValidationError):
        ScenarioRequest(question="Pregunta", year=year, unrealismLevel="realista")


@pytest.mark.parametrize("level", ["realista", "ilusionante", "descerebrado"])
def test_request_accepts_only_documented_levels(level):
    request = ScenarioRequest(question="Pregunta", year=2026, unrealismLevel=level)

    assert request.unrealismLevel == level


@pytest.mark.parametrize("level", ["Realista", "fantástico", "", None])
def test_request_rejects_unknown_level(level):
    with pytest.raises(ValidationError):
        ScenarioRequest(question="Pregunta", year=2026, unrealismLevel=level)