"""
screenshot.py — takes a screenshot on command, saves it with a timestamp.
pyautogui is imported lazily (needs a display to even import) so this module
can be imported safely on headless setups; only fails when actually called
without a display, with a clear message instead of crashing on import.
"""
from datetime import datetime
from pathlib import Path

SHOTS_DIR = Path(__file__).resolve().parent.parent / "data" / "screenshots"


def take_screenshot() -> str:
    try:
        import pyautogui
    except Exception as e:
        return f"Screenshot lene ke liye display chahiye — kaam nahi kiya: {e}"

    SHOTS_DIR.mkdir(parents=True, exist_ok=True)
    path = SHOTS_DIR / f"screenshot-{datetime.now().strftime('%Y%m%d-%H%M%S')}.png"
    img = pyautogui.screenshot()
    img.save(path)
    return str(path)
