"""
app_launcher.py — open any application or website by name/voice command.
Cross-platform: Windows, macOS, Linux.
"""

import platform
import subprocess
import webbrowser

OS = platform.system()

# Common app name -> actual launch command, per OS. Add your own favorites here.
APP_MAP = {
    "windows": {
        "notepad": "notepad.exe", "calculator": "calc.exe", "paint": "mspaint.exe",
        "word": "winword.exe", "excel": "excel.exe", "powerpoint": "powerpnt.exe",
        "chrome": "chrome.exe", "vscode": "code.exe", "explorer": "explorer.exe",
        "spotify": "spotify.exe", "terminal": "wt.exe", "settings": "start ms-settings:",
    },
    "darwin": {
        "notes": "Notes", "calculator": "Calculator", "safari": "Safari",
        "chrome": "Google Chrome", "vscode": "Visual Studio Code", "terminal": "Terminal",
        "finder": "Finder", "spotify": "Spotify", "word": "Microsoft Word",
    },
    "linux": {
        "terminal": "gnome-terminal", "files": "nautilus", "chrome": "google-chrome",
        "vscode": "code", "calculator": "gnome-calculator", "settings": "gnome-control-center",
        "spotify": "spotify",
    },
}


def open_app(name: str) -> str:
    name = name.lower().strip()
    key = "windows" if OS == "Windows" else ("darwin" if OS == "Darwin" else "linux")
    target = APP_MAP.get(key, {}).get(name)

    try:
        if OS == "Windows":
            subprocess.Popen(target or name, shell=True)
        elif OS == "Darwin":
            subprocess.Popen(["open", "-a", target or name])
        else:
            subprocess.Popen([target or name])
        return f"{name} khol diya."
    except Exception as e:
        return f"'{name}' open nahi ho saka: {e}"


def open_website(url: str) -> str:
    if not url.startswith("http"):
        url = "https://" + url
    webbrowser.open(url)
    return f"{url} khol diya."


if __name__ == "__main__":
    print(open_app("notepad"))
