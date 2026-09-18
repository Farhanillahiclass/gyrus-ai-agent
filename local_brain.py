"""
local_brain.py — Gyrus's AI brain, running 100% locally. No API key. No internet
required once set up. No data ever leaves this PC.

Honest technical note: training a language model completely from scratch
(the way a real from-zero "apna trained engine" would work) needs millions of
dollars of GPUs and billions of words of data — not realistic on a personal
laptop. What IS realistic, and what this file does, is run an already-trained
*open-weights* model (Qwen2.5, Llama 3.2, Phi-3, etc. — all free to download
and use) directly on your machine via llama-cpp-python. There is no server,
no API, no key, no per-message cost, no rate limit, and no internet needed
after the one-time model download. This is the same technique tools like
LM Studio and GPT4All use under the hood.

One-time setup:
    python download_model.py   (downloads the model file automatically, no API key)
    pip install llama-cpp-python   (the engine that runs it — see requirements.txt)
"""

from pathlib import Path
from modules import user_profile

MODELS_DIR = Path(__file__).resolve().parent / "models"
_llm = None
_history = []

BASE_SYSTEM_PROMPT = """You are "Gyrus", a warm, capable personal assistant running fully offline on the user's own PC.
Reply in whichever language the user used — Urdu script, Roman Urdu, or English — mirroring their style.
Keep answers concise and clear. You do not control the computer directly — other code handles that."""

def _system_prompt() -> str:
    summary = user_profile.profile_summary()
    return BASE_SYSTEM_PROMPT + ("\n" + summary if summary else "")


def _find_model_file() -> Path:
    if not MODELS_DIR.exists():
        return None
    ggufs = list(MODELS_DIR.glob("*.gguf"))
    return ggufs[0] if ggufs else None


def _load():
    global _llm
    if _llm is not None:
        return _llm

    try:
        from llama_cpp import Llama
    except ImportError:
        raise RuntimeError(
            "llama-cpp-python isn't installed. Run: pip install llama-cpp-python\n"
            "(this is a C++ compile — on Windows it needs 'Desktop development with "
            "C++' from the Visual Studio Build Tools if the plain pip install fails)"
        )

    model_path = _find_model_file()
    if not model_path:
        raise FileNotFoundError(
            "No .gguf model found in models/. Run: python download_model.py"
        )
    _llm = Llama(
        model_path=str(model_path),
        n_ctx=4096,
        n_threads=max(2, (__import__("os").cpu_count() or 4) - 1),
        verbose=False,
    )
    return _llm


def ask(user_text: str) -> str:
    """Send a message to the local model and return its reply. Fully offline."""
    try:
        llm = _load()
    except (FileNotFoundError, RuntimeError) as e:
        return str(e)

    _history.append({"role": "user", "content": user_text})
    messages = [{"role": "system", "content": _system_prompt()}] + _history[-20:]

    result = llm.create_chat_completion(messages=messages, max_tokens=500, temperature=0.6)
    reply = result["choices"][0]["message"]["content"].strip()
    _history.append({"role": "assistant", "content": reply})
    return reply


if __name__ == "__main__":
    print("Gyrus LOCAL brain (no internet, no API). Type 'exit' to quit.")
    while True:
        q = input("You: ")
        if q.strip().lower() == "exit":
            break
        print("Gyrus:", ask(q))
