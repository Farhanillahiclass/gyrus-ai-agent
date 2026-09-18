"""
study_tracker.py — logs daily study sessions and computes a performance_index,
directly adapted from the feature-engineering idea in Farhan's own project:
student-performance-eda-feature-engineering
(github.com/Farhanillahiclass/student-performance-eda-feature-engineering),
which found attendance + prior score were the strongest predictors of passing.

performance_index here = weighted composite of:
  - consistency (% of last 14 days with a logged study session)
  - study_efficiency (self-rated understanding per hour studied)
  - momentum (trend: are you studying more or less than last week?)
"""

import json
from datetime import datetime, timedelta
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "study_log.json"


def _load():
    if not DATA_FILE.exists():
        return []
    try:
        return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []


def _save(log):
    DATA_FILE.parent.mkdir(exist_ok=True)
    DATA_FILE.write_text(json.dumps(log, indent=2, ensure_ascii=False), encoding="utf-8")


def log_session(subject: str, hours: float, understanding_rating: int):
    """understanding_rating: 1-10, how well you feel you understood the material."""
    log = _load()
    log.append({
        "date": datetime.now().strftime("%Y-%m-%d"),
        "subject": subject,
        "hours": hours,
        "understanding": max(1, min(10, understanding_rating)),
    })
    _save(log)
    return "Study session log ho gaya."


def performance_index() -> dict:
    log = _load()
    if not log:
        return {"performance_index": 0, "note": "Abhi koi study session log nahi hui."}

    today = datetime.now().date()
    last_14 = [e for e in log if (today - datetime.strptime(e["date"], "%Y-%m-%d").date()).days <= 14]
    last_7 = [e for e in log if (today - datetime.strptime(e["date"], "%Y-%m-%d").date()).days <= 7]
    prev_7 = [e for e in log if 7 < (today - datetime.strptime(e["date"], "%Y-%m-%d").date()).days <= 14]

    days_with_session_14 = len({e["date"] for e in last_14})
    consistency = (days_with_session_14 / 14) * 100

    total_hours_14 = sum(e["hours"] for e in last_14) or 1
    weighted_understanding = sum(e["hours"] * e["understanding"] for e in last_14) / total_hours_14
    study_efficiency = (weighted_understanding / 10) * 100

    hours_last_7 = sum(e["hours"] for e in last_7)
    hours_prev_7 = sum(e["hours"] for e in prev_7) or hours_last_7 or 1
    momentum_ratio = hours_last_7 / hours_prev_7
    momentum = min(100, momentum_ratio * 50)  # 50 = same as last week, 100 = doubled+

    index = round(0.4 * consistency + 0.4 * study_efficiency + 0.2 * momentum)

    return {
        "performance_index": index,
        "consistency_pct": round(consistency),
        "study_efficiency_pct": round(study_efficiency),
        "momentum_pct": round(momentum),
        "hours_last_7_days": round(hours_last_7, 1),
    }


GOAL_FILE = Path(__file__).resolve().parent.parent / "data" / "study_goal.json"


def set_weekly_goal(hours: float):
    GOAL_FILE.parent.mkdir(exist_ok=True)
    GOAL_FILE.write_text(json.dumps({"hours_per_week": hours}), encoding="utf-8")
    return f"Weekly goal set to {hours} hours."


def get_weekly_goal() -> dict:
    if not GOAL_FILE.exists():
        return {"hours_per_week": None}
    try:
        return json.loads(GOAL_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"hours_per_week": None}


def weekly_progress() -> dict:
    """Compares hours actually logged this week against the goal."""
    goal = get_weekly_goal().get("hours_per_week")
    log = _load()
    today = datetime.now().date()
    week_start = today - timedelta(days=today.weekday())
    hours_this_week = sum(
        e["hours"] for e in log
        if datetime.strptime(e["date"], "%Y-%m-%d").date() >= week_start
    )
    result = {"hours_logged": round(hours_this_week, 1), "goal_hours": goal}
    if goal:
        result["progress_pct"] = round(min(100, (hours_this_week / goal) * 100))
    return result


def generate_quiz(subject: str, ask_fn) -> str:
    """Asks the configured AI brain to generate a short quiz on `subject` —
    a lightweight way to self-test without needing any dedicated quiz
    content or a trained model of its own."""
    prompt = (
        f"Generate a short 5-question quiz on the subject '{subject}' to help a student "
        f"self-test their understanding. Mix in short-answer and multiple-choice questions. "
        f"Put the answer key at the end, clearly separated. Keep it concise."
    )
    return ask_fn(prompt)


if __name__ == "__main__":
    log_session("Math", 2, 7)
    print(performance_index())
