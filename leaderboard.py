import json
from pathlib import Path

_FILE = Path(__file__).parent / "leaderboard.json"
_MAX_ENTRIES = 10


def load_scores() -> list[dict]:
    if not _FILE.exists():
        return []
    try:
        return json.loads(_FILE.read_text())
    except (json.JSONDecodeError, OSError):
        return []


def save_scores(scores: list[dict]) -> None:
    _FILE.write_text(json.dumps(scores, indent=2))


def is_high_score(score: int) -> bool:
    scores = load_scores()
    if len(scores) < _MAX_ENTRIES:
        return True
    return score > min(s["score"] for s in scores)


def add_score(name: str, score: int) -> list[dict]:
    scores = load_scores()
    scores.append({"name": name[:3].upper(), "score": score})
    scores.sort(key=lambda s: s["score"], reverse=True)
    scores = scores[:_MAX_ENTRIES]
    save_scores(scores)
    return scores


def top_scores(n: int = 10) -> list[dict]:
    return load_scores()[:n]


def wipe_scores() -> None:
    save_scores([])