"""
server.py — local backend for the 3D dashboard. Runs entirely on your PC
(default http://localhost:8765). The dashboard talks to this over plain HTTP
on localhost only — nothing leaves your machine, no cloud, no API.

Run:
    python server.py
Then open dashboard/index.html in your browser.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn

import commands
import brain
from modules import (
    tasks, study_tracker, diet_planner, system_control, screenshot, brightness,
    whatsapp, email_manager, vision, file_organizer, file_search, app_launcher, clipboard,
    user_profile, social_analysis, research, youtube_control, document_analysis,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    tasks.start_reminder_thread(speak_fn=None)
    yield

app = FastAPI(title="Gyrus Local Backend", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])


@app.exception_handler(Exception)
async def friendly_error_handler(request, exc):
    """Any unhandled error in any route (missing hardware, missing credentials,
    a library that needs a display, etc.) comes back as a normal JSON reply
    the dashboard can show, instead of a raw 500 that breaks the UI."""
    from fastapi.responses import JSONResponse
    return JSONResponse(status_code=200, content={"reply": f"Feature error: {exc}", "error": True})


class Message(BaseModel):
    text: str

class ReminderInfo(BaseModel):
    text: str
    priority: str = "Medium"
    remind_at: Optional[str] = None

class SystemAction(BaseModel):
    action: str            # lock | sleep | screenshot | brightness | restart | shutdown
    value: Optional[int] = None
    confirmed: bool = False

class StudyLog(BaseModel):
    subject: str
    hours: float
    understanding: int

class DietRequest(BaseModel):
    weight_kg: float
    height_cm: float
    age: int
    sex: str
    activity_level: str = "moderate"
    goal: str = "maintain"
    suggest_meals: bool = False

class WhatsAppMessage(BaseModel):
    phone_number: str
    message: str

class EmailSend(BaseModel):
    to_address: str
    subject: str
    body: str

class OCRRequest(BaseModel):
    image_path: str

class FileTask(BaseModel):
    action: str        # organize | find | open_app | open_website | clipboard_write
    target: Optional[str] = None
    value: Optional[str] = None

class ProfileFact(BaseModel):
    key: str
    value: str

class ProfileNote(BaseModel):
    text: str

class SocialAnalyzeRequest(BaseModel):
    url: str

class ResearchRequest(BaseModel):
    topic: str

class RenameRequest(BaseModel):
    path: str
    new_name: str

class MoveRequest(BaseModel):
    path: str
    destination: str

class SuggestNameRequest(BaseModel):
    path: str

class StudyGoalRequest(BaseModel):
    hours_per_week: float

class QuizRequest(BaseModel):
    subject: str

class YoutubeAction(BaseModel):
    action: str

class DocAnalyzeRequest(BaseModel):
    path: str
    question: str = "Summarize this document clearly."


@app.get("/api/status")
def status():
    return {"status": "online", "engine": "local", "provider": brain.PROVIDER}


# ---------------- Profile / memory ----------------
@app.get("/api/profile")
def get_profile():
    return {"name": user_profile.get_fact("name"), "notes": user_profile.all_notes()}

@app.post("/api/profile/fact")
def set_profile_fact(fact: ProfileFact):
    user_profile.set_fact(fact.key, fact.value)
    return {"ok": True}

@app.post("/api/profile/note")
def add_profile_note(note: ProfileNote):
    user_profile.remember_note(note.text)
    return {"ok": True}

@app.post("/api/profile/analyze")
def analyze_social(req: SocialAnalyzeRequest):
    return {"reply": social_analysis.analyze_profile(req.url, ask_fn=brain.ask)}


@app.post("/api/message")
def send_message(msg: Message):
    def no_confirm(prompt): return False
    def no_ask(prompt): return None
    reply = commands.handle(msg.text, confirm_fn=no_confirm, ask_fn=no_ask)
    return {"reply": reply}


# ---------------- Tasks ----------------
@app.get("/api/tasks")
def get_tasks():
    return {"tasks": tasks.list_tasks(), "summary": tasks.summary()}

@app.post("/api/tasks/add")
def add_task(info: ReminderInfo):
    return {"task": tasks.add_task(info.text, priority=info.priority, remind_at=info.remind_at)}

@app.post("/api/tasks/{task_id}/complete")
def complete_task(task_id: int):
    tasks.complete_task(task_id); return {"ok": True}

@app.delete("/api/tasks/{task_id}")
def delete_task(task_id: int):
    tasks.delete_task(task_id); return {"ok": True}


# ---------------- System control ----------------
@app.post("/api/system")
def system_action(a: SystemAction):
    if a.action == "lock":
        system_control.lock_pc(); return {"reply": "PC lock ho gaya."}
    if a.action == "sleep":
        system_control.sleep_pc(); return {"reply": "Sleep mode."}
    if a.action == "screenshot":
        path = screenshot.take_screenshot(); return {"reply": f"Saved: {path}", "path": path}
    if a.action == "brightness" and a.value is not None:
        return {"reply": brightness.set_brightness(a.value)}
    if a.action == "restart":
        if not a.confirmed:
            return {"reply": "Confirmation required.", "needs_confirm": True}
        system_control.restart_pc(); return {"reply": "Restarting..."}
    if a.action == "shutdown":
        if not a.confirmed:
            return {"reply": "Confirmation required.", "needs_confirm": True}
        system_control.shutdown_pc(); return {"reply": "Shutting down..."}
    return {"reply": f"Unknown action: {a.action}"}


# ---------------- Study tracker ----------------
@app.get("/api/study/performance")
def get_performance():
    return study_tracker.performance_index()

@app.post("/api/study/log")
def log_study(entry: StudyLog):
    study_tracker.log_session(entry.subject, entry.hours, entry.understanding)
    return {"ok": True}


# ---------------- Diet planner ----------------
@app.post("/api/diet/calculate")
def calculate_diet(req: DietRequest):
    macros = diet_planner.calculate_calories(
        req.weight_kg, req.height_cm, req.age, req.sex, req.activity_level, req.goal
    )
    meal_suggestion = None
    if req.suggest_meals:
        prompt = diet_planner.build_meal_plan_prompt(macros)
        meal_suggestion = brain.ask(prompt)
    return {"macros": macros, "meal_suggestion": meal_suggestion}


# ---------------- WhatsApp ----------------
@app.post("/api/whatsapp/send")
def whatsapp_send(msg: WhatsAppMessage):
    try:
        whatsapp.send_now(msg.phone_number, msg.message)
        return {"reply": "WhatsApp message bhej diya (browser tab check karein)."}
    except Exception as e:
        return {"reply": f"WhatsApp send fail ho gaya: {e}"}


# ---------------- Email ----------------
@app.get("/api/email/unread")
def email_unread():
    return {"messages": email_manager.get_unread()}

@app.post("/api/email/send")
def email_send(req: EmailSend):
    result = email_manager.send_email(req.to_address, req.subject, req.body)
    return {"reply": result}


# ---------------- Vision / OCR ----------------
@app.post("/api/vision/ocr")
def vision_ocr(req: OCRRequest):
    text = vision.read_text_from_image(req.image_path)
    return {"text": text}

@app.post("/api/documents/analyze")
def analyze_document_endpoint(req: DocAnalyzeRequest):
    return {"reply": document_analysis.analyze_document(req.path, req.question, ask_fn=brain.ask)}


# ---------------- File tools ----------------
@app.post("/api/tools")
def file_tools(req: FileTask):
    if req.action == "organize":
        import os
        target = req.target or os.path.expanduser("~/Downloads")
        result = file_organizer.organize(target)
        return {"reply": "Organized: " + ", ".join(f"{k} {v}" for k, v in result.items() if v)}
    if req.action == "find":
        matches = file_search.find_files(req.target or "")
        return {"reply": "; ".join(matches[:10]) if matches else "Koi file nahi mili.", "matches": matches}
    if req.action == "open_app":
        return {"reply": app_launcher.open_app(req.target or "")}
    if req.action == "open_website":
        return {"reply": app_launcher.open_website(req.target or "")}
    if req.action == "clipboard_write":
        return {"reply": clipboard.copy_text(req.value or "")}
    if req.action == "clipboard_read":
        return {"reply": clipboard.read_clipboard() or "Clipboard khali hai."}
    return {"reply": f"Unknown tool action: {req.action}"}


# ---------------- System info ----------------
@app.get("/api/system/info")
def system_info():
    return system_control.get_system_info()

@app.get("/api/system/processes")
def system_processes():
    return {"processes": system_control.list_top_processes()}


# ---------------- YouTube extras ----------------
@app.post("/api/youtube")
def youtube_action(req: YoutubeAction):
    actions = {
        "speed_up": youtube_control.speed_up, "speed_down": youtube_control.speed_down,
        "captions": youtube_control.toggle_captions, "theater": youtube_control.toggle_theater_mode,
    }
    fn = actions.get(req.action)
    if not fn:
        return {"reply": f"Unknown YouTube action: {req.action}"}
    fn()
    return {"reply": f"Done: {req.action}"}


# ---------------- Research ----------------
@app.post("/api/research/deep")
def deep_research_endpoint(req: ResearchRequest):
    result = research.deep_research(req.topic, ask_fn=brain.ask)
    return result

@app.get("/api/research/download/{filename}")
def download_research(filename: str):
    from fastapi.responses import FileResponse
    path = research.RESEARCH_DIR / filename
    if not path.exists():
        return {"error": "File not found"}
    return FileResponse(path, filename=filename, media_type="text/markdown")


# ---------------- File rename/move/suggest ----------------
@app.post("/api/files/rename")
def rename_file_endpoint(req: RenameRequest):
    return {"reply": file_organizer.rename_file(req.path, req.new_name)}

@app.post("/api/files/move")
def move_file_endpoint(req: MoveRequest):
    return {"reply": file_organizer.move_file(req.path, req.destination)}

@app.post("/api/files/suggest-name")
def suggest_name_endpoint(req: SuggestNameRequest):
    return file_organizer.suggest_name_from_content(req.path, ask_fn=brain.ask)


# ---------------- Study extras ----------------
@app.post("/api/study/goal")
def set_study_goal(req: StudyGoalRequest):
    return {"reply": study_tracker.set_weekly_goal(req.hours_per_week)}

@app.get("/api/study/progress")
def study_progress():
    return study_tracker.weekly_progress()

@app.post("/api/study/quiz")
def study_quiz(req: QuizRequest):
    return {"quiz": study_tracker.generate_quiz(req.subject, ask_fn=brain.ask)}


# ---------------- Real-time reminders (dashboard polling) ----------------
@app.get("/api/tasks/due")
def tasks_due():
    return {"due": tasks.due_now_unshown(mark_shown=True)}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8765)
