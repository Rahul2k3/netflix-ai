"""Pydantic schemas used across CineSage AI."""
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class Movie(BaseModel):
    """Structured representation of a movie extracted from free text."""

    title: str = Field(description="The title of the movie")
    release_year: Optional[int] = Field(
        default=None, description="The year the movie was released"
    )
    genre: List[str] = Field(
        default_factory=list, description="List of genres, e.g. ['Sci-Fi', 'Drama']"
    )
    director: Optional[str] = Field(default=None, description="The director's name")
    cast: List[str] = Field(default_factory=list, description="Main cast members")
    rating: Optional[float] = Field(
        default=None, description="Rating out of 10, if mentioned in the text"
    )
    summary: str = Field(description="A concise 1-2 sentence summary of the plot")

    @field_validator("rating")
    @classmethod
    def rating_in_range(cls, v):
        if v is not None and not (0 <= v <= 10):
            raise ValueError("rating must be between 0 and 10")
        return v

    @field_validator("release_year")
    @classmethod
    def year_is_reasonable(cls, v):
        if v is not None and not (1888 <= v <= 2100):
            raise ValueError("release_year looks invalid")
        return v


class SimilarMovie(BaseModel):
    """A single recommended movie, with a reason it was suggested."""

    title: str = Field(description="Title of the recommended movie")
    release_year: Optional[int] = Field(default=None)
    reason: str = Field(description="One sentence on why it's similar")


class Recommendations(BaseModel):
    """A list of similar-movie recommendations returned by the LLM."""

    recommendations: List[SimilarMovie]
