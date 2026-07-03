"""Core extraction logic: turns a free-text paragraph into a structured Movie."""
import logging
from typing import Optional

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_mistralai import ChatMistralAI

from cinesage.schema import Movie

logger = logging.getLogger(__name__)

_EXTRACTION_PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "You are a precise movie-data extraction engine.\n"
     "Extract movie information from the paragraph below.\n"
     "If a field is not mentioned in the text, leave it empty rather than guessing.\n"
     "{format_instructions}"),
    ("human", "{paragraph}"),
])


def get_model(temperature: float = 0.0) -> ChatMistralAI:
    """Create the LLM client. temperature=0 keeps extraction deterministic."""
    return ChatMistralAI(model="mistral-small-2506", temperature=temperature)


def extract_movie(paragraph: str, model: Optional[ChatMistralAI] = None, retries: int = 2) -> Movie:
    """Extract a structured Movie from a free-text paragraph.

    Args:
        paragraph: Free text describing a movie.
        model: Optional pre-built chat model (mainly used to inject a fake
            model in tests). Defaults to a fresh ChatMistralAI client.
        retries: How many extra attempts to make if the model's output
            doesn't parse into a valid Movie.

    Raises:
        ValueError: if paragraph is empty.
        RuntimeError: if the model output could not be parsed after retries.
    """
    if not paragraph or not paragraph.strip():
        raise ValueError("paragraph must not be empty")

    model = model or get_model()
    parser = PydanticOutputParser(pydantic_object=Movie)

    last_error = None
    for attempt in range(1, retries + 2):
        try:
            final_prompt = _EXTRACTION_PROMPT.invoke({
                "paragraph": paragraph,
                "format_instructions": parser.get_format_instructions(),
            })
            response = model.invoke(final_prompt)
            return parser.parse(response.content)
        except Exception as exc:  # noqa: BLE001 - retry on any parse/API error
            last_error = exc
            logger.warning("Extraction attempt %d/%d failed: %s", attempt, retries + 1, exc)

    raise RuntimeError(f"Failed to extract movie after {retries + 1} attempt(s): {last_error}")
