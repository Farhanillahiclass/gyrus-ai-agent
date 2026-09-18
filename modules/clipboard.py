"""
clipboard.py — read/write the system clipboard by voice/text command.
Wrapped in try/except because pyperclip needs a working clipboard mechanism
(xclip/xsel on Linux, or a display) — without one it raises, which would
otherwise crash the whole request instead of giving a clear message.
"""
import pyperclip


def copy_text(text: str):
    try:
        pyperclip.copy(text)
        return "Clipboard mein copy ho gaya."
    except Exception as e:
        return f"Clipboard access nahi mila: {e}"


def read_clipboard() -> str:
    try:
        return pyperclip.paste()
    except Exception as e:
        return f"Clipboard access nahi mila: {e}"
