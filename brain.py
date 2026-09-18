"""
brain.py — Gyrus's AI brain router.

Default is "local" — a model file that runs entirely on your PC via
llama-cpp-python. Zero API calls, zero per-message cost, works with no
internet once downloaded. Run `python download_model.py` once (no API key
needed — it's a public file download) and you're set.

This was switched back from Hugging Face's cloud API after that API proved
unreliable in practice — a real trade-off either way: cloud APIs need no
download but depend on a working internet connection and a working key;
local needs a one-time download (handled by download_model.py) but then
runs completely offline and never depends on any external service again.
"""

import os
from dotenv import load_dotenv

load_dotenv()
PROVIDER = os.getenv("AI_PROVIDER", "local").lower()  # local (default) | huggingface | gemini | anthropic


def ask(user_text: str) -> str:
    if PROVIDER == "local":
        import local_brain
        return local_brain.ask(user_text)
    elif PROVIDER == "huggingface":
        import cloud_brain
        return cloud_brain.ask_huggingface(user_text)
    elif PROVIDER == "gemini":
        import cloud_brain
        return cloud_brain.ask_gemini(user_text)
    elif PROVIDER == "anthropic":
        import cloud_brain
        return cloud_brain.ask_anthropic(user_text)
    else:
        return f"Unknown AI_PROVIDER '{PROVIDER}' — use 'local', 'huggingface', 'gemini', or 'anthropic'."


if __name__ == "__main__":
    print(f"Gyrus brain ({PROVIDER}). Type 'exit' to quit.")
    while True:
        q = input("You: ")
        if q.strip().lower() == "exit":
            break
        print("Gyrus:", ask(q))
