"""
youtube_control.py — voice-activated YouTube search/play + playback control.

Search & play: uses pywhatkit, which opens your default browser and searches/
plays the first result — no API key, no login needed.

Play/Pause/Mute/Seek/Fullscreen/Volume: sent as the same keyboard shortcuts
YOU would press on the YouTube tab (these are YouTube's own hotkeys) — so the
YouTube tab must be the active/focused window when you give a playback command.
That's a real limitation of controlling a browser tab from outside without a
browser extension — worth knowing, not hidden.

Note: pyautogui/pywhatkit are imported lazily inside each function (not at
module load time) because they require a display (X server on Linux) to even
import — importing them eagerly would crash this whole module (and anything
that imports it, including the dashboard backend) on headless/no-GUI setups.
"""

import time


def play(query: str):
    """Search and play the first YouTube result for `query`."""
    import pywhatkit
    print(f"[youtube] Playing: {query}")
    pywhatkit.playonyt(query)
    time.sleep(3)


def toggle_play_pause():
    import pyautogui
    pyautogui.press("k")


def stop():
    import pyautogui
    pyautogui.press("k")  # YouTube has no native "stop"; pause instead


def mute():
    import pyautogui
    pyautogui.press("m")


def unmute():
    import pyautogui
    pyautogui.press("m")


def next_video():
    import pyautogui
    pyautogui.hotkey("shift", "n")


def previous_video():
    import pyautogui
    pyautogui.hotkey("shift", "p")


def seek_forward(seconds: int = 10):
    import pyautogui
    for _ in range(max(1, seconds // 5)):
        pyautogui.press("l")


def seek_backward(seconds: int = 10):
    import pyautogui
    for _ in range(max(1, seconds // 5)):
        pyautogui.press("j")


def volume_up(steps: int = 5):
    import pyautogui
    for _ in range(steps):
        pyautogui.press("up")


def volume_down(steps: int = 5):
    import pyautogui
    for _ in range(steps):
        pyautogui.press("down")


def toggle_fullscreen():
    import pyautogui
    pyautogui.press("f")


def speed_up():
    """YouTube hotkey: shift+. increases playback speed one step."""
    import pyautogui
    pyautogui.hotkey("shift", ".")


def speed_down():
    """YouTube hotkey: shift+, decreases playback speed one step."""
    import pyautogui
    pyautogui.hotkey("shift", ",")


def toggle_captions():
    import pyautogui
    pyautogui.press("c")


def toggle_theater_mode():
    import pyautogui
    pyautogui.press("t")


def search_only(query: str):
    """Opens YouTube search results for `query` WITHOUT auto-playing the
    first video — useful when you want to pick from a list yourself rather
    than have Gyrus guess which result you meant."""
    import webbrowser
    import urllib.parse
    url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}"
    webbrowser.open(url)


if __name__ == "__main__":
    play("sufi music")
