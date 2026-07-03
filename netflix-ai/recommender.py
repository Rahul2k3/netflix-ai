"""Chained LLM call: given an extracted Movie, recommend similar movies.

This is the second "hop" in the pipeline — it demonstrates prompt chaining
(feeding one structured LLM output into a second LLM call) rather than a
single one-shot prompt.
"""
import logging
from typing import Optional

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_mistralai import ChatMistralAI

from cinesage.schema import Movie, Recommendations
from cinesage.extractor import get_model

logger = logging.getLogger(__name__)

_RECOMMEND_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "You are a knowledgeable film critic.\n"
     "Given details about a movie, suggest exactly 3 similar movies the "
     "viewer might enjoy. Do not recommend the same movie.\n"
     "{format_instructions}"),
    ("human", "Movie: {title} ({year})\nGenres: {genres}\nSummary: {summary}"),
])


def recommend_similar(movie: Movie, model: Optional[ChatMistralAI] = None) -> Recommendations:
    """Given an extracted Movie, ask the LLM for 3 similar recommendations."""
    model = model or get_model(temperature=0.7)
    parser = PydanticOutputParser(pydantic_object=Recommendations)

    final_prompt = _RECOMMEND_PROMPT.invoke({
        "title": movie.title,
        "year": movie.release_year or "unknown",
        "genres": ", ".join(movie.genre) or "unknown",
        "summary": movie.summary,
        "format_instructions": parser.get_format_instructions(),
    })

    response = model.invoke(final_prompt)
    return parser.parse(response.content)
