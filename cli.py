"""Command-line interface for CineSage AI.

Usage:
    python cli.py --text "A paragraph describing a movie..."
    python cli.py --file movies.txt                 # one paragraph per line
    python cli.py --file movies.txt --recommend      # also fetch recommendations
    python cli.py --text "..." --out result.json     # save output to a file
"""
import argparse
import json
import logging
import sys

from cinesage.extractor import extract_movie
from cinesage.recommender import recommend_similar

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def process_paragraph(paragraph: str, want_recommendations: bool) -> dict:
    movie = extract_movie(paragraph)
    result = movie.model_dump()
    if want_recommendations:
        recs = recommend_similar(movie)
        result["recommendations"] = [r.model_dump() for r in recs.recommendations]
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract structured movie data from text using AI.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--text", help="A single paragraph describing a movie")
    group.add_argument("--file", help="Path to a text file, one movie paragraph per line")
    parser.add_argument("--recommend", action="store_true", help="Also generate similar-movie recommendations")
    parser.add_argument("--out", help="Optional path to write JSON results")
    args = parser.parse_args()

    if args.text:
        paragraphs = [args.text]
    else:
        with open(args.file, "r", encoding="utf-8") as f:
            paragraphs = [line.strip() for line in f if line.strip()]

    results = []
    for i, para in enumerate(paragraphs, start=1):
        print(f"\n[{i}/{len(paragraphs)}] Extracting...")
        try:
            result = process_paragraph(para, args.recommend)
            results.append(result)
            print(json.dumps(result, indent=2))
        except (ValueError, RuntimeError) as exc:
            print(f"  Failed: {exc}", file=sys.stderr)

    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2)
        print(f"\nSaved {len(results)} result(s) to {args.out}")


if __name__ == "__main__":
    main()
