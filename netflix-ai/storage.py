"""Save/load extraction history and export it to CSV for the Streamlit UI."""
import json
import csv
import io
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

HISTORY_FILE = Path("history.json")


def append_to_history(movie_dict: Dict[str, Any], path: Path = HISTORY_FILE) -> None:
    """Append one extracted movie (as a dict) to the local JSON history file."""
    history = load_history(path)
    record = dict(movie_dict)
    record["extracted_at"] = datetime.now().isoformat(timespec="seconds")
    history.append(record)
    path.write_text(json.dumps(history, indent=2), encoding="utf-8")


def load_history(path: Path = HISTORY_FILE) -> List[Dict[str, Any]]:
    """Load extraction history from disk, returning an empty list if none exists."""
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def history_to_csv_bytes(history: List[Dict[str, Any]]) -> bytes:
    """Convert history records to CSV bytes, ready for a Streamlit download button."""
    if not history:
        return b""
    buffer = io.StringIO()
    fieldnames = list(history[0].keys())
    writer = csv.DictWriter(buffer, fieldnames=fieldnames)
    writer.writeheader()
    for row in history:
        row_copy = row.copy()
        for key, value in row_copy.items():
            if isinstance(value, list):
                row_copy[key] = "; ".join(str(v) for v in value)
        writer.writerow(row_copy)
    return buffer.getvalue().encode("utf-8")
