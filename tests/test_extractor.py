"""Tests for the extraction pipeline.

A fake model is injected so these tests run offline, with no API key and
no network calls — this is what lets them run in CI.
"""
from unittest.mock import MagicMock
import pytest

from cinesage.extractor import extract_movie


class _FakeResponse:
    def __init__(self, content):
        self.content = content


def test_extract_movie_empty_paragraph_raises():
    with pytest.raises(ValueError):
        extract_movie("")


def test_extract_movie_parses_valid_json():
    fake_model = MagicMock()
    fake_model.invoke.return_value = _FakeResponse(
        '{"title": "Inception", "release_year": 2010, "genre": ["Sci-Fi"], '
        '"director": "Christopher Nolan", "cast": ["Leonardo DiCaprio"], '
        '"rating": 8.8, "summary": "A thief steals secrets via dreams."}'
    )
    movie = extract_movie("Inception is a 2010 movie...", model=fake_model)
    assert movie.title == "Inception"
    assert movie.release_year == 2010
    assert movie.rating == 8.8


def test_extract_movie_retries_then_raises_on_repeated_failure():
    fake_model = MagicMock()
    fake_model.invoke.side_effect = Exception("API error")
    with pytest.raises(RuntimeError):
        extract_movie("Some paragraph about a film.", model=fake_model, retries=1)
    # 1 initial attempt + 1 retry = 2 calls
    assert fake_model.invoke.call_count == 2
