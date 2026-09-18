"""
notes.py — voice-to-text note taking. Keeps listening and appending to a
Word document (or plain .txt) until the user says a stop phrase.
"""

from datetime import datetime
from pathlib import Path
from docx import Document

NOTES_DIR = Path(__file__).resolve().parent.parent / "data" / "notes"
STOP_PHRASES = {"stop recording", "recording band karo", "band karo", "stop note"}


def dictate(listen_fn, speak_fn, filename: str = None) -> str:
    """
    listen_fn: function() -> str, e.g. voice.listen
    speak_fn: function(str), e.g. voice.speak
    Returns the path to the saved .docx file.
    """
    NOTES_DIR.mkdir(parents=True, exist_ok=True)
    filename = filename or f"note-{datetime.now().strftime('%Y%m%d-%H%M%S')}.docx"
    path = NOTES_DIR / filename

    doc = Document()
    doc.add_heading(f"Gyrus Note — {datetime.now().strftime('%d %b %Y, %H:%M')}", level=1)

    speak_fn("Bolna shuru karein — jab khatam ho, 'stop recording' boliye.")
    while True:
        chunk = listen_fn()
        if not chunk:
            continue
        if chunk.strip().lower() in STOP_PHRASES:
            speak_fn("Note save ho gaya.")
            break
        doc.add_paragraph(chunk)
        print(f"[note] + {chunk}")

    doc.save(path)
    return str(path)


if __name__ == "__main__":
    import voice  # noqa (only for standalone testing)
    dictate(voice.listen, voice.speak)
