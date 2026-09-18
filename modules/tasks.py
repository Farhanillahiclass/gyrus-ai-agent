"""
tasks.py — task manager & reminders, upgraded with the architecture from
Farhan's own taskflow-cli project (github.com/Farhanillahiclass/taskflow-cli):
priority levels, atomic JSON writes, custom exceptions, search/filter/sort,
and overdue detection — now wired into Gyrus's voice/text commands plus
background spoken reminders (taskflow-cli itself has no voice layer; that
part is new here).
"""

import json
import os
import tempfile
import threading
import time
from datetime import datetime
from pathlib import Path

DATA_FILE = Path(__file__).resolve().parent.parent / "data" / "tasks.json"
PRIORITY_ORDER = {"High": 3, "Medium": 2, "Low": 1}


class TaskError(Exception):
    pass


class ValidationError(TaskError):
    pass


class TaskNotFoundError(TaskError):
    pass


def _load():
    if not DATA_FILE.exists():
        return []
    try:
        return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []


def _save(tasks):
    """Atomic write: write to a temp file then replace, so a crash mid-write
    never corrupts tasks.json."""
    DATA_FILE.parent.mkdir(exist_ok=True)
    fd, tmp_path = tempfile.mkstemp(dir=DATA_FILE.parent, suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        json.dump(tasks, f, indent=2, ensure_ascii=False)
    os.replace(tmp_path, DATA_FILE)


def add_task(text: str, priority: str = "Medium", remind_at: str = None) -> dict:
    if not text or not text.strip():
        raise ValidationError("Task text khali nahi ho sakta.")
    if priority not in PRIORITY_ORDER:
        priority = "Medium"

    tasks = _load()
    next_id = (max((t["id"] for t in tasks), default=0)) + 1
    task = {
        "id": next_id,
        "text": text.strip(),
        "priority": priority,
        "remind_at": remind_at,   # 'YYYY-MM-DD HH:MM' or None
        "done": False,
        "notified": False,
        "created": datetime.now().isoformat(timespec="minutes"),
    }
    tasks.append(task)
    _save(tasks)
    return task


def list_tasks(include_done=False, sort_by="priority") -> list:
    tasks = _load()
    if not include_done:
        tasks = [t for t in tasks if not t["done"]]
    if sort_by == "priority":
        tasks.sort(key=lambda t: PRIORITY_ORDER.get(t["priority"], 0), reverse=True)
    elif sort_by == "due":
        tasks.sort(key=lambda t: t.get("remind_at") or "9999")
    return tasks


def search_tasks(keyword: str) -> list:
    keyword = keyword.lower()
    return [t for t in _load() if keyword in t["text"].lower()]


def overdue_tasks() -> list:
    now = datetime.now()
    result = []
    for t in _load():
        if t["done"] or not t.get("remind_at"):
            continue
        try:
            due = datetime.strptime(t["remind_at"], "%Y-%m-%d %H:%M")
        except ValueError:
            continue
        if due < now:
            result.append(t)
    return result


def _find(tasks, task_id):
    for t in tasks:
        if t["id"] == task_id:
            return t
    raise TaskNotFoundError(f"Task ID {task_id} nahi mila.")


def complete_task(task_id: int) -> bool:
    tasks = _load()
    _find(tasks, task_id)["done"] = True
    _save(tasks)
    return True


def delete_task(task_id: int) -> bool:
    tasks = _load()
    _find(tasks, task_id)  # raises if not found
    tasks = [t for t in tasks if t["id"] != task_id]
    _save(tasks)
    return True


def due_now_unshown(mark_shown: bool = False) -> list:
    """Tasks whose reminder time has arrived. Used by the dashboard's polling
    loop for real-time popup/spoken alerts while the dashboard is open — a
    parallel path to the CLI's background TTS thread, using a separate
    'shown_on_dashboard' flag so the two surfaces don't suppress each other's
    alerts (finishing the CLI reminder shouldn't silently skip the dashboard
    one, and vice versa)."""
    tasks_list = _load()
    now = datetime.now()
    due = []
    changed = False
    for t in tasks_list:
        if t.get("remind_at") and not t.get("done") and not t.get("shown_on_dashboard"):
            try:
                remind_time = datetime.strptime(t["remind_at"], "%Y-%m-%d %H:%M")
            except ValueError:
                continue
            if now >= remind_time:
                due.append(t)
                if mark_shown:
                    t["shown_on_dashboard"] = True
                    changed = True
    if changed:
        _save(tasks_list)
    return due


def summary() -> dict:
    tasks = _load()
    pending = [t for t in tasks if not t["done"]]
    return {
        "total": len(tasks),
        "pending": len(pending),
        "done": len(tasks) - len(pending),
        "overdue": len(overdue_tasks()),
        "high_priority_pending": len([t for t in pending if t["priority"] == "High"]),
    }


# ---------------- background spoken reminders ----------------

def _reminder_loop(speak_fn):
    try:
        from plyer import notification
        has_plyer = True
    except ImportError:
        has_plyer = False

    while True:
        tasks = _load()
        now = datetime.now()
        changed = False
        for t in tasks:
            if t.get("remind_at") and not t.get("notified") and not t.get("done"):
                try:
                    due = datetime.strptime(t["remind_at"], "%Y-%m-%d %H:%M")
                except ValueError:
                    continue
                if now >= due:
                    msg = f"Sir, aap ka task pending hai: {t['text']}"
                    if has_plyer:
                        try:
                            notification.notify(title="Gyrus Reminder", message=t["text"], timeout=10)
                        except Exception:
                            pass
                    if speak_fn:
                        speak_fn(msg)
                    else:
                        print(f"[reminder] {msg}")
                    t["notified"] = True
                    changed = True
        if changed:
            _save(tasks)
        time.sleep(30)


def start_reminder_thread(speak_fn=None):
    t = threading.Thread(target=_reminder_loop, args=(speak_fn,), daemon=True)
    t.start()
    return t


if __name__ == "__main__":
    add_task("Submit assignment", priority="High", remind_at="2026-09-13 18:00")
    print(list_tasks())
    print(summary())
