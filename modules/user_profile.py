"""
user_profile.py — Gyrus's local memory about you. Plain JSON on your own
disk (data/user_profile.json) — never sent anywhere, never cloud-synced.
This is what lets Gyrus greet you by name and recall things you've told it
to remember, across restarts, instead of "starting fresh" every session.
"""

import json
from pathlib import Path
from datetime import datetime

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "user_profile.json"


def _load() -> dict:
    if not DATA_FILE.exists():
        return {"facts": {}, "notes": []}
    try:
        return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"facts": {}, "notes": []}


def _save(data: dict):
    DATA_FILE.parent.mkdir(exist_ok=True)
    DATA_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def set_fact(key: str, value: str):
    """Store a single named fact, e.g. set_fact('name', 'Farhan')."""
    data = _load()
    data["facts"][key] = value
    _save(data)


def get_fact(key: str, default=None):
    return _load()["facts"].get(key, default)


def remember_note(text: str):
    """Store a free-form thing the user asked Gyrus to remember."""
    data = _load()
    data["notes"].append({"text": text, "saved": datetime.now().isoformat(timespec="minutes")})
    _save(data)


def all_notes() -> list:
    return _load()["notes"]


def is_known_user() -> bool:
    return bool(get_fact("name"))


def profile_summary() -> str:
    """A short text block to hand to the AI brain so it has context about
    the user, without dumping the whole raw JSON into every prompt."""
    data = _load()
    if not data["facts"] and not data["notes"]:
        return ""
    parts = []
    if data["facts"]:
        parts.append("Known facts about the user: " + "; ".join(f"{k}={v}" for k, v in data["facts"].items()))
    if data["notes"]:
        recent = data["notes"][-10:]
        parts.append("Things the user asked to be remembered: " + "; ".join(n["text"] for n in recent))
    return " | ".join(parts)


if __name__ == "__main__":
    set_fact("name", "Farhan")
    remember_note("Prefers Roman Urdu mixed with English")
    print(profile_summary())
