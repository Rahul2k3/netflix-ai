"""CineSage AI — Streamlit UI for AI-powered movie info extraction."""
import json

import streamlit as st
from dotenv import load_dotenv

from cinesage.extractor import extract_movie, get_model
from cinesage.recommender import recommend_similar
from cinesage.schema import Movie
from cinesage.storage import history_to_csv_bytes

load_dotenv()

st.set_page_config(page_title="CineSage AI", page_icon="🎬", layout="wide")

EXAMPLE = (
    "Inception is a 2010 sci-fi thriller directed by Christopher Nolan, "
    "starring Leonardo DiCaprio, Joseph Gordon-Levitt, and Elliot Page. "
    "It follows a thief who steals secrets through dream-sharing technology. "
    "It's widely rated around 8.8/10."
)

# ---------------- Session state ----------------
if "history" not in st.session_state:
    st.session_state.history = []          # list of movie dicts, most recent last
if "recommendations" not in st.session_state:
    st.session_state.recommendations = {}  # title -> list of rec dicts
if "paragraph_input" not in st.session_state:
    st.session_state.paragraph_input = ""


def _fill_example() -> None:
    st.session_state.paragraph_input = EXAMPLE


@st.cache_resource
def _model():
    return get_model()


def render_movie_card(movie: dict, key_prefix: str) -> None:
    with st.container(border=True):
        col1, col2 = st.columns([1, 3])
        with col1:
            st.markdown("<div style='font-size:48px;text-align:center'>🎬</div>", unsafe_allow_html=True)
            if movie.get("rating") is not None:
                st.metric("Rating", f"{movie['rating']}/10")
        with col2:
            year = f" ({movie['release_year']})" if movie.get("release_year") else ""
            st.subheader(f"{movie['title']}{year}")
            if movie.get("genre"):
                st.write(" ".join(f"`{g}`" for g in movie["genre"]))
            if movie.get("director"):
                st.caption(f"🎥 Directed by {movie['director']}")
            if movie.get("cast"):
                st.caption(f"⭐ Starring {', '.join(movie['cast'][:5])}")
            st.write(movie.get("summary", ""))

        if st.button("🔎 Find Similar Movies", key=f"rec_{key_prefix}"):
            with st.spinner("Thinking of similar movies..."):
                try:
                    recs = recommend_similar(Movie(**movie), model=_model())
                    st.session_state.recommendations[movie["title"]] = [
                        r.model_dump() for r in recs.recommendations
                    ]
                except Exception as exc:  # noqa: BLE001
                    st.error(f"Could not fetch recommendations: {exc}")

        recs = st.session_state.recommendations.get(movie["title"])
        if recs:
            st.markdown("**Because you liked this, you might enjoy:**")
            for r in recs:
                r_year = f" ({r['release_year']})" if r.get("release_year") else ""
                st.markdown(f"- **{r['title']}{r_year}** — {r['reason']}")


# ---------------- Sidebar: history + export ----------------
with st.sidebar:
    st.header("📜 History")
    st.caption(f"{len(st.session_state.history)} movie(s) extracted this session")

    if st.session_state.history:
        csv_bytes = history_to_csv_bytes(st.session_state.history)
        st.download_button("⬇️ Download CSV", csv_bytes, file_name="cinesage_history.csv", mime="text/csv")
        st.download_button(
            "⬇️ Download JSON",
            json.dumps(st.session_state.history, indent=2).encode("utf-8"),
            file_name="cinesage_history.json",
            mime="application/json",
        )
        if st.button("🗑️ Clear History"):
            st.session_state.history = []
            st.session_state.recommendations = {}
            st.rerun()

        st.divider()
        for m in reversed(st.session_state.history):
            st.write(f"• {m['title']}")
    else:
        st.info("Extract a movie to see it here.")

# ---------------- Main ----------------
st.title("🎬 CineSage AI")
st.caption("Paste a movie description — AI extracts structured data and suggests similar films.")

st.text_area("Movie description", height=150, key="paragraph_input", placeholder=EXAMPLE)

col_a, col_b = st.columns([1, 5])
with col_a:
    extract_clicked = st.button("✨ Extract", type="primary")
with col_b:
    st.button("Try an example", on_click=_fill_example)

if extract_clicked:
    paragraph = st.session_state.paragraph_input
    if not paragraph or not paragraph.strip():
        st.warning("Please paste a movie description first.")
    else:
        with st.spinner("Analyzing with AI..."):
            try:
                movie = extract_movie(paragraph, model=_model())
                movie_dict = movie.model_dump()
                st.session_state.history.append(movie_dict)
                st.success("Extraction complete!")
                render_movie_card(movie_dict, key_prefix=str(len(st.session_state.history)))
            except ValueError as exc:
                st.warning(str(exc))
            except RuntimeError as exc:
                st.error(f"The AI couldn't extract structured data: {exc}")

elif st.session_state.history:
    st.divider()
    st.subheader("Recent extractions")
    for i, m in enumerate(reversed(st.session_state.history[-5:])):
        render_movie_card(m, key_prefix=f"hist_{i}")
