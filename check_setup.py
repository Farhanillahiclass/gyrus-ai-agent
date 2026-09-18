"""
check_setup.py — run this FIRST if anything fails to start. It tells you
exactly what's missing instead of a raw Python traceback.

    python check_setup.py

This exists because of two real errors seen while testing on Windows:
  1. Running the dashboard HTML file as a bash/terminal command (it's a
     webpage — open it by double-clicking it in File Explorer, or dragging
     it into your browser, not by typing its path in a terminal).
  2. "ModuleNotFoundError: No module named 'fastapi'" — requirements.txt
     hadn't been installed into the Python environment actually being used
     (Windows users: make sure your venv is ACTIVATED before pip install —
     check for "(venv)" at the start of your terminal prompt).
"""

import importlib
import sys

REQUIRED = {
    "requests": "requests", "dotenv": "python-dotenv",
    "speech_recognition": "SpeechRecognition", "pyttsx3": "pyttsx3",
    "pywhatkit": "pywhatkit", "pyautogui": "pyautogui", "pyperclip": "pyperclip",
    "psutil": "psutil", "docx": "python-docx", "schedule": "schedule",
    "plyer": "plyer", "keyring": "keyring", "numpy": "numpy",
    "fastapi": "fastapi", "uvicorn": "uvicorn", "pydantic": "pydantic",
    "sklearn": "scikit-learn", "pandas": "pandas", "joblib": "joblib",
    "screen_brightness_control": "screen-brightness-control",
}
OPTIONAL = {
    "llama_cpp": "llama-cpp-python (needed for the local AI brain)",
    "cv2": "opencv-contrib-python-headless (needed for vision.py / OCR)",
    "pytesseract": "pytesseract (needed for vision.py / OCR)",
    "playwright": "playwright (needed for auto_login.py / social_post.py)",
    "pygetwindow": "pygetwindow (Windows/Mac window management)",
}


def check(modules: dict, required: bool):
    missing = []
    for import_name, pip_name in modules.items():
        try:
            importlib.import_module(import_name)
        except Exception:
            missing.append(pip_name)
    return missing


def main():
    print(f"Python: {sys.version.split()[0]} at {sys.executable}\n")

    missing_req = check(REQUIRED, required=True)
    missing_opt = check(OPTIONAL, required=False)

    if not missing_req:
        print("✅ All required packages are installed.")
    else:
        print("❌ MISSING required packages — Gyrus will crash without these:")
        for m in missing_req:
            print(f"   - {m}")
        print(f"\n   Fix: pip install {' '.join(missing_req)}")
        print("   (Windows: make sure your venv is activated first — you should")
        print("    see '(venv)' at the start of your terminal prompt)")

    if missing_opt:
        print("\n⚠️  Optional packages not installed (only needed for specific features):")
        for m in missing_opt:
            print(f"   - {m}")

    import os
    model_dir = os.path.join(os.path.dirname(__file__), "models")
    ggufs = [f for f in os.listdir(model_dir) if f.endswith(".gguf")] if os.path.isdir(model_dir) else []
    if ggufs:
        print(f"\n✅ Local AI model found: {ggufs[0]}")
    else:
        print("\n⚠️  No .gguf model in models/ yet — run: python download_model.py")
        print("    (one command, no API key needed, ~2GB, one-time)")
        print("    Everything else — tasks, YouTube, system control, etc. — works without it.")

    print("\n" + "=" * 60)
    import os as _os
    from dotenv import load_dotenv
    load_dotenv()
    provider = _os.getenv("AI_PROVIDER", "local")
    print(f"AI_PROVIDER = {provider}")
    if provider == "local" and not ggufs:
        print("⚠️  Run 'python download_model.py' to enable chat (other features work without it).")
    if provider == "huggingface" and not _os.getenv("HUGGINGFACE_API_KEY"):
        print("⚠️  No HUGGINGFACE_API_KEY set — chat won't work until you add one.")
        print("    Free token: https://huggingface.co/settings/tokens (needs 'Make calls to Inference Providers')")
    print("=" * 60)
    print("To run Gyrus:")
    print("  CLI:       python main.py          (or: python main.py --text)")
    print("  Dashboard: python server.py        <- then OPEN dashboard/index.html")
    print("             by double-clicking it in File Explorer / Finder,")
    print("             NOT by typing its path into a terminal.")
    print("=" * 60)


if __name__ == "__main__":
    main()
