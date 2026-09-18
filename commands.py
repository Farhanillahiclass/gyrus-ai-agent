"""
commands.py — the single command router. Both main.py (voice/text CLI) and
server.py (backend for the 3D dashboard) call handle() so command logic
exists in exactly one place.
"""

import re
from pathlib import Path

import brain
from modules import (
    youtube_control, system_control, file_organizer, tasks, notes, research,
    app_launcher, clipboard, screenshot, window_manager, brightness, file_search,
    vision, diet_planner, study_tracker, intent_classifier, user_profile, social_analysis,
    document_analysis,
)

CONFIRM_WORDS = {"yes", "haan", "ha", "confirm", "ok", "theek hai"}


def handle(cmd: str, confirm_fn=None, ask_fn=None) -> str:
    """
    confirm_fn: function(prompt:str) -> bool, used before destructive actions
                (restart/shutdown). If None, destructive actions are skipped
                for safety and a message is returned instead.
    ask_fn: function(prompt:str) -> str, used to collect one extra piece of
            info (e.g. a reminder time). If None, that feature is skipped
            with a message asking the caller to provide it directly.
    Returns the reply text (caller decides whether to speak/display it).
    """
    low = cmd.lower().strip()

    def confirm(prompt):
        return confirm_fn(prompt) if confirm_fn else False

    # ---- Memory: name capture & "remember this" ----
    m = re.search(r"my name is (.+)", low) or re.search(r"mera na+m (.+?) h[ae]i?$", low)
    if m:
        name = m.group(1).strip().title()
        user_profile.set_fact("name", name)
        return f"Theek hai {name}, yaad rakh liya."
    m = re.search(r"remember that (.+)", low) or re.search(r"ye+? yaad rakh(?:na|o)?\s*(?:ke)?\s*(.+)", low)
    if m and "task" not in low and "remind me" not in low:
        user_profile.remember_note(m.group(1).strip())
        return "Yaad rakh liya."
    if "what do you know about me" in low or "mere baare mein kya" in low:
        summary = user_profile.profile_summary()
        return summary if summary else "Abhi tak aapke baare mein kuch save nahi hua — mujhe apna naam bata dein."

    # ---- Social profile analysis ----
    m = re.search(r"analyz[e]?\s+(?:my\s+)?(?:linkedin|github|profile|site)\s*[:\-]?\s*(https?://\S+|\S+\.\S+)", cmd, re.I)
    if m:
        return social_analysis.analyze_profile(m.group(1).strip(), ask_fn=brain.ask)

    # ---- Document/PDF/image analysis ----
    m = re.search(r"(?:analyze|summarize|read) (?:this |the )?(?:document|pdf|file) (.+)", cmd, re.I)
    if m:
        return document_analysis.analyze_document(m.group(1).strip(), "Summarize this document clearly.", ask_fn=brain.ask)

    # ---- YouTube / media ----
    if re.search(r"play .* (on )?youtube|play .*(song|music|video)", low):
        query = re.sub(r"play|on youtube|youtube", "", low).strip()
        youtube_control.play(query or "music")
        return f"{query} chala diya."
    if low in ("pause", "resume", "play/pause", "toggle play"):
        youtube_control.toggle_play_pause(); return "Theek hai."
    if "mute" in low and "unmute" not in low:
        youtube_control.mute(); return "Mute kar diya."
    if "unmute" in low:
        youtube_control.unmute(); return "Unmute kar diya."
    if "next video" in low or "skip" in low:
        youtube_control.next_video(); return "Next video."
    if "previous video" in low or "last video" in low:
        youtube_control.previous_video(); return "Previous video."
    if "forward" in low:
        youtube_control.seek_forward(10); return "Forward kar diya."
    if "rewind" in low or "backward" in low:
        youtube_control.seek_backward(10); return "Rewind kar diya."
    if "volume up" in low:
        youtube_control.volume_up(); return "Volume up."
    if "volume down" in low:
        youtube_control.volume_down(); return "Volume down."
    if "full screen" in low or "fullscreen" in low:
        youtube_control.toggle_fullscreen(); return "Fullscreen toggle kar diya."

    # ---- System control ----
    if "lock" in low and ("pc" in low or "computer" in low or "system" in low):
        system_control.lock_pc(); return "PC lock ho gaya."
    if "restart" in low:
        if confirm("Pakka restart karna hai?"):
            system_control.restart_pc(); return "Restart ho raha hai."
        return "Restart cancel kar diya."
    if "shutdown" in low or "shut down" in low:
        if confirm("Pakka shutdown karna hai?"):
            system_control.shutdown_pc(); return "Shutdown ho raha hai."
        return "Shutdown cancel kar diya."
    if low == "go to sleep" or ("sleep" in low and "pc" in low):
        system_control.sleep_pc(); return "Sleep mode mein ja raha hai."
    m = re.search(r"volume (?:ko |ku )?(\d{1,3})", low)
    if m and "youtube" not in low:
        system_control.set_volume(int(m.group(1))); return f"System volume {m.group(1)}% set kar diya."

    # ---- App / website launcher ----
    m = re.search(r"open (.+)", low)
    if m and "youtube" not in low and "download" not in low:
        target = m.group(1).strip()
        if "." in target or "website" in low:
            return app_launcher.open_website(target.replace("website", "").strip())
        return app_launcher.open_app(target)

    # ---- File organizer / search ----
    if "organize" in low and ("download" in low or "desktop" in low or "folder" in low):
        target = str(Path.home() / ("Downloads" if "download" in low else "Desktop"))
        result = file_organizer.organize(target)
        return "Files organize ho gaye: " + ", ".join(f"{k} {v}" for k, v in result.items() if v)
    m = re.search(r"find (?:the )?file (.+)", low) or re.search(r"search for file (.+)", low)
    if m:
        matches = file_search.find_files(m.group(1).strip())
        return "Mile: " + "; ".join(matches[:5]) if matches else "Koi file nahi mili."

    # ---- Clipboard / screenshot / windows / brightness ----
    if "copy" in low and "clipboard" in low:
        return clipboard.copy_text(cmd.split("copy", 1)[-1].strip())
    if "clipboard" in low and ("read" in low or "paste" in low):
        return clipboard.read_clipboard() or "Clipboard khali hai."
    if "screenshot" in low:
        path = screenshot.take_screenshot()
        return f"Screenshot save ho gaya: {path}"
    if "minimize" in low:
        return window_manager.minimize_active()
    if "maximize" in low:
        return window_manager.maximize_active()
    if "close window" in low or low == "close this":
        return window_manager.close_active()
    m = re.search(r"switch to (.+)", low)
    if m:
        return window_manager.switch_to(m.group(1).strip())
    m = re.search(r"brightness (?:ko |ku )?(\d{1,3})", low)
    if m:
        return brightness.set_brightness(int(m.group(1)))

    # ---- Tasks / reminders ----
    if low.startswith("remind me") or "remind me to" in low:
        priority = "High" if "urgent" in low or "important" in low else "Medium"
        when = ask_fn("Kis waqt yaad dilaun? (YYYY-MM-DD HH:MM, ya 'no time')") if ask_fn else None
        remind_at = None if (not when or "no time" in when.lower()) else when
        tasks.add_task(cmd, priority=priority, remind_at=remind_at)
        return "Theek hai, yaad rakh liya."
    if "show my tasks" in low or "show tasks" in low or "list tasks" in low:
        pending = tasks.list_tasks()
        return "Aap ke pending tasks: " + "; ".join(f"[{t['priority']}] {t['text']}" for t in pending) if pending else "Koi pending task nahi hai."
    if "task summary" in low or "executive summary" in low:
        s = tasks.summary()
        return f"Total {s['total']}, pending {s['pending']}, overdue {s['overdue']}, high-priority pending {s['high_priority_pending']}."

    # ---- Notes ----
    if "take a note" in low or "start dictation" in low:
        return "note-dictation-trigger"  # main.py handles this specially (needs continuous listening loop)

    # ---- Weather / news / research ----
    if "weather" in low or "mausam" in low:
        return research.get_weather()
    if low.startswith("news") or "khabrain" in low:
        topic = low.replace("news about", "").replace("news", "").strip() or "Pakistan"
        headlines = research.get_news(topic)
        return "Top headlines: " + "; ".join(h["title"] for h in headlines[:3])
    if low.startswith("search for") or low.startswith("research"):
        query = re.sub(r"search for|research", "", low, count=1).strip()
        return research.web_search_summary(query, ask_fn=brain.ask)

    # ---- Vision (OCR / face detection on an image path) ----
    m = re.search(r"read text (?:from|in) (.+)", low) or re.search(r"ocr (.+)", low)
    if m:
        return vision.read_text_from_image(m.group(1).strip())

    # ---- Diet planner ----
    if "diet plan" in low or "meal plan" in low or "calorie" in low:
        return ("Diet plan ke liye ye info chahiye: weight (kg), height (cm), age, gender, "
                "activity level (sedentary/light/moderate/active/very_active), aur goal "
                "(lose/maintain/gain). Ye sab ek sath bata dein.")

    # ---- Study tracker ----
    if "study performance" in low or "performance index" in low:
        p = study_tracker.performance_index()
        return f"Performance index: {p.get('performance_index')} — consistency {p.get('consistency_pct','-')}%, efficiency {p.get('study_efficiency_pct','-')}%."
    m = re.search(r"log study (.+?) (\d+(?:\.\d+)?) hours understanding (\d+)", low)
    if m:
        study_tracker.log_session(m.group(1).strip(), float(m.group(2)), int(m.group(3)))
        return "Study session log ho gayi."

    # ---- Trained intent classifier (Gyrus's own model, catches paraphrases
    #      the regexes above missed) — before falling through to the AI brain ----
    intent, confidence = intent_classifier.predict(cmd)
    if intent:
        routed = _route_intent(intent, cmd, confirm)
        if routed is not None:
            return routed

    # ---- Fallback: local AI brain (chit-chat, general Q&A, coding, math) ----
    # ---- Deep research (Wikipedia + Semantic Scholar + AI synthesis, saved as a file) ----
    m = re.search(r"deep research (?:on |about )?(.+)", low) or re.search(r"research paper (?:on |about )?(.+)", low)
    if m:
        result = research.deep_research(m.group(1).strip(), ask_fn=brain.ask)
        return f"Research article ban gaya aur save ho gaya: {result['file_path']}\n\n{result['article'][:500]}..."

    # ---- File/folder rename & move ----
    m = re.search(r"rename (.+?) to (.+)", cmd, re.I)
    if m:
        return file_organizer.rename_file(m.group(1).strip(), m.group(2).strip())
    m = re.search(r"move (.+?) to (.+)", cmd, re.I)
    if m:
        return file_organizer.move_file(m.group(1).strip(), m.group(2).strip())
    m = re.search(r"suggest (?:a )?(?:better )?name for (.+)", cmd, re.I)
    if m:
        result = file_organizer.suggest_name_from_content(m.group(1).strip(), ask_fn=brain.ask)
        if "error" in result:
            return result["error"]
        return f"Suggested name: {result['suggested']} (original: {result['original']}) — say 'rename {result['path']} to {result['suggested']}' to apply it."

    # ---- System info ----
    if "system info" in low or "cpu usage" in low or "ram usage" in low or "battery" in low:
        info = system_control.get_system_info()
        parts = [f"CPU {info['cpu_percent']}%", f"RAM {info['ram_percent']}% ({info['ram_used_gb']}/{info['ram_total_gb']} GB)", f"Disk {info['disk_percent']}%"]
        if "battery_percent" in info:
            parts.append(f"Battery {info['battery_percent']}%")
        return ", ".join(parts)

    # ---- YouTube extras ----
    if "speed up" in low or "playback speed" in low and "up" in low:
        youtube_control.speed_up(); return "Speed badha diya."
    if "slow down" in low or "playback speed" in low and "down" in low:
        youtube_control.speed_down(); return "Speed kam kar diya."
    if "caption" in low or "subtitle" in low:
        youtube_control.toggle_captions(); return "Captions toggle kar diye."
    if "theater mode" in low:
        youtube_control.toggle_theater_mode(); return "Theater mode toggle kar diya."

    # ---- Study extras ----
    m = re.search(r"set (?:my )?(?:weekly )?study goal (?:to )?(\d+(?:\.\d+)?)", low)
    if m:
        return study_tracker.set_weekly_goal(float(m.group(1)))
    if "study progress" in low or "weekly progress" in low:
        p = study_tracker.weekly_progress()
        return f"{p['hours_logged']} hours logged this week" + (f", goal {p['goal_hours']}h ({p['progress_pct']}%)" if p.get('goal_hours') else ".")
    m = re.search(r"quiz me on (.+)", low) or re.search(r"quiz (?:on |about )?(.+)", low)
    if m:
        return study_tracker.generate_quiz(m.group(1).strip(), ask_fn=brain.ask)

    return brain.ask(cmd)


def _route_intent(intent: str, cmd: str, confirm) -> str:
    """Maps a classifier-predicted intent to an actual action, for phrasing
    that didn't match any regex above. Returns None for intents better left
    to the AI brain (greeting/chitchat) or that need info regex can't extract
    reliably (task_add needs a time; diet_plan needs numbers) — those fall
    through to the normal guided replies already defined above."""
    if intent == "youtube_play":
        query = re.sub(r"youtube|play|chalao|lagao|par|pe|kholo", "", cmd, flags=re.I).strip()
        youtube_control.play(query or "music")
        return f"{query or 'Music'} chala diya."
    if intent == "system_lock":
        system_control.lock_pc(); return "PC lock ho gaya."
    if intent == "system_restart":
        if confirm("Pakka restart karna hai?"):
            system_control.restart_pc(); return "Restart ho raha hai."
        return "Restart cancel kar diya."
    if intent == "system_shutdown":
        if confirm("Pakka shutdown karna hai?"):
            system_control.shutdown_pc(); return "Shutdown ho raha hai."
        return "Shutdown cancel kar diya."
    if intent == "system_sleep":
        system_control.sleep_pc(); return "Sleep mode mein ja raha hai."
    if intent == "screenshot":
        path = screenshot.take_screenshot(); return f"Screenshot save ho gaya: {path}"
    if intent == "organize_files":
        target = str(Path.home() / "Downloads")
        result = file_organizer.organize(target)
        return "Files organize ho gaye: " + ", ".join(f"{k} {v}" for k, v in result.items() if v)
    if intent == "task_list":
        pending = tasks.list_tasks()
        return "Aap ke pending tasks: " + "; ".join(f"[{t['priority']}] {t['text']}" for t in pending) if pending else "Koi pending task nahi hai."
    if intent == "task_summary":
        s = tasks.summary()
        return f"Total {s['total']}, pending {s['pending']}, overdue {s['overdue']}, high-priority pending {s['high_priority_pending']}."
    if intent == "weather":
        return research.get_weather()
    if intent == "news":
        headlines = research.get_news("Pakistan")
        return "Top headlines: " + "; ".join(h["title"] for h in headlines[:3])
    if intent == "research":
        return research.web_search_summary(cmd, ask_fn=brain.ask)
    if intent == "study_performance":
        p = study_tracker.performance_index()
        return f"Performance index: {p.get('performance_index')} — consistency {p.get('consistency_pct','-')}%, efficiency {p.get('study_efficiency_pct','-')}%."
    if intent == "diet_plan":
        return ("Diet plan ke liye ye info chahiye: weight (kg), height (cm), age, gender, "
                "activity level (sedentary/light/moderate/active/very_active), aur goal "
                "(lose/maintain/gain). Ye sab ek sath bata dein.")
    if intent in ("find_file", "task_add", "open_app"):
        return None  # needs a follow-up question the AI brain handles more naturally
    return None  # greeting, chitchat -> let brain.ask handle it directly
