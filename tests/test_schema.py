"""Tests for CineSage schema validation."""
import pytest
from pydantic import ValidationError

from cinesage.schema import Movie


def test_movie_minimal_valid():
    m = Movie(title="Inception", genre=["Sci-Fi"], cast=["Leonardo DiCaprio"], summary="A dream heist.")
    assert m.title == "Inception"
    assert m.release_year is None


def test_movie_rating_out_of_range_rejected():
    with pytest.raises(ValidationError):
        Movie(title="X", genre=[], cast=[], summary="s", rating=15)


def test_movie_year_out_of_range_rejected():
    with pytest.raises(ValidationError):
        Movie(title="X", genre=[], cast=[], summary="s", release_year=1500)


def test_movie_valid_rating_accepted():
    m = Movie(title="X", genre=[], cast=[], summary="s", rating=8.8)
    assert m.rating == 8.8
