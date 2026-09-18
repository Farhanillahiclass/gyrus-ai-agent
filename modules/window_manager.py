"""
window_manager.py — minimize/maximize/close/switch windows by voice command.
Full support on Windows/macOS via pygetwindow; Linux support is best-effort
(depends on desktop environment — wmctrl is the most reliable fallback).
"""

import platform
import subprocess

OS = platform.system()

try:
    import pygetwindow as gw
    HAS_GW = OS in ("Windows", "Darwin")
except Exception:
    # pygetwindow raises NotImplementedError (not ImportError) on Linux —
    # catching broadly so this module still imports fine everywhere;
    # Linux just falls through to the wmctrl path in each function below.
    HAS_GW = False


def minimize_active():
    if HAS_GW:
        win = gw.getActiveWindow()
        if win:
            win.minimize()
            return "Minimize kar diya."
    elif OS == "Linux":
        subprocess.run(["wmctrl", "-r", ":ACTIVE:", "-b", "add,hidden"])
        return "Minimize kar diya."
    return "Window minimize nahi ho saki."


def maximize_active():
    if HAS_GW:
        win = gw.getActiveWindow()
        if win:
            win.maximize()
            return "Maximize kar diya."
    elif OS == "Linux":
        subprocess.run(["wmctrl", "-r", ":ACTIVE:", "-b", "add,maximized_vert,maximized_horz"])
        return "Maximize kar diya."
    return "Window maximize nahi ho saki."


def close_active():
    if HAS_GW:
        win = gw.getActiveWindow()
        if win:
            win.close()
            return "Band kar diya."
    elif OS == "Linux":
        subprocess.run(["wmctrl", "-c", ":ACTIVE:"])
        return "Band kar diya."
    return "Window band nahi ho saki."


def switch_to(title_substring: str):
    if HAS_GW:
        for w in gw.getWindowsWithTitle(title_substring):
            w.activate()
            return f"{title_substring} par switch kar diya."
        return f"'{title_substring}' naam ki koi window nahi mili."
    elif OS == "Linux":
        subprocess.run(["wmctrl", "-a", title_substring])
        return f"{title_substring} par switch kar diya."
    return "Window switch nahi ho saki."
