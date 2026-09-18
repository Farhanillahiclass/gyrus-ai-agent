"""
cloud_brain.py — engines that call an external API instead of running locally.

ask_huggingface() is the DEFAULT conversational engine as of this version —
Hugging Face's free Inference API, chosen specifically because it needs no
multi-GB model download and puts no extra load on your PC (per an explicit
request to avoid a heavy local download). Being transparent about the
trade-off: this IS a real external API call — your messages go to Hugging
Face's servers. If you'd rather have zero external calls at the cost of a
one-time model download, switch AI_PROVIDER=local in .env (see local_brain.py).

ask_gemini() / ask_anthropic() remain as further opt-in alternatives.
"""

import os
import requests
from dotenv import load_dotenv
from modules import user_profile

load_dotenv()
HF_KEY = os.getenv("HUGGINGFACE_API_KEY", "")
HF_MODEL = os.getenv("HUGGINGFACE_MODEL", "Qwen/Qwen2.5-7B-Instruct")
GEMINI_KEY = os.getenv("GEMINI_API_KEY", "")
ANTHROPIC_KEY = os.getenv("ANTHROPIC_API_KEY", "")
USER_NAME = os.getenv("USER_NAME", "there")


def _system_prompt() -> str:
    base = f"""You are "Gyrus", a personal assistant for {USER_NAME}.
Reply in whichever language the user used — Urdu script, Roman Urdu, or English."""
    summary = user_profile.profile_summary()
    return base + ("\n" + summary if summary else "")


_history = []


def ask_huggingface(user_text: str) -> str:
    if not HF_KEY:
        return ("HUGGINGFACE_API_KEY missing in .env — get a free token at "
                "https://huggingface.co/settings/tokens (needs 'Make calls to Inference Providers' permission) and add it to .env")

    # Hugging Face moved to a single unified router endpoint for all chat
    # models (replacing the old per-model api-inference.huggingface.co URL,
    # which now returns connection/404-style errors for many models). This
    # is the current, correct endpoint as of this update.
    url = "https://router.huggingface.co/v1/chat/completions"
    headers = {"Authorization": f"Bearer {HF_KEY}", "Content-Type": "application/json"}
    messages = [{"role": "system", "content": _system_prompt()}]
    messages += [{"role": t["role"], "content": t["text"]} for t in _history[-20:]]
    messages.append({"role": "user", "content": user_text})

    try:
        resp = requests.post(url, headers=headers, json={"model": HF_MODEL, "messages": messages, "max_tokens": 500}, timeout=45)
        resp.raise_for_status()
        data = resp.json()
        reply = data["choices"][0]["message"]["content"]
    except requests.exceptions.HTTPError as e:
        if resp.status_code == 401:
            return "Hugging Face rejected the token — check it has 'Make calls to Inference Providers' permission enabled at https://huggingface.co/settings/tokens"
        if resp.status_code == 503:
            return "Model warming up on Hugging Face's free tier — this can take ~20-30s on the first request. Try again in a moment."
        return f"Hugging Face API error ({resp.status_code}): {resp.text[:200]}"
    except requests.exceptions.RequestException as e:
        return f"Couldn't reach Hugging Face (network issue): {e}"
    except (KeyError, IndexError):
        return "Couldn't parse Hugging Face reply: " + str(data)[:300]

    _history.append({"role": "user", "text": user_text})
    _history.append({"role": "assistant", "text": reply})
    return reply


def ask_gemini(user_text: str) -> str:
    if not GEMINI_KEY:
        return "GEMINI_API_KEY missing in .env"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_KEY}"
    contents = [{"role": t["role"], "parts": [{"text": t["text"]}]} for t in _history[-20:]]
    contents.append({"role": "user", "parts": [{"text": user_text}]})
    resp = requests.post(url, json={"system_instruction": {"parts": [{"text": _system_prompt()}]}, "contents": contents}, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    try:
        reply = data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError):
        return "Couldn't parse Gemini reply: " + str(data)[:300]
    _history.append({"role": "user", "text": user_text})
    _history.append({"role": "model", "text": reply})
    return reply


def ask_anthropic(user_text: str) -> str:
    if not ANTHROPIC_KEY:
        return "ANTHROPIC_API_KEY missing in .env"
    headers = {"x-api-key": ANTHROPIC_KEY, "anthropic-version": "2023-06-01", "content-type": "application/json"}
    messages = [{"role": t["role"], "content": t["text"]} for t in _history[-20:]]
    messages.append({"role": "user", "content": user_text})
    payload = {"model": "claude-sonnet-4-6", "max_tokens": 1000, "system": _system_prompt(), "messages": messages}
    resp = requests.post("https://api.anthropic.com/v1/messages", headers=headers, json=payload, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    reply = "".join(b.get("text", "") for b in data.get("content", []) if b.get("type") == "text")
    _history.append({"role": "user", "text": user_text})
    _history.append({"role": "assistant", "text": reply})
    return reply
