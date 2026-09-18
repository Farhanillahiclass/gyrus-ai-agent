"""
brightness.py — set screen brightness by voice command.
"""
import screen_brightness_control as sbc


def set_brightness(percent: int) -> str:
    percent = max(0, min(100, percent))
    try:
        sbc.set_brightness(percent)
        return f"Brightness {percent}% set ho gayi."
    except Exception as e:
        return f"Brightness set nahi ho saki: {e}"
