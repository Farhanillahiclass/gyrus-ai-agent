"""
social_analysis.py — fetches a public social/portfolio profile (GitHub,
LinkedIn's public page, a personal site, etc.) and asks the configured AI
brain to summarize it and suggest improvements.

Honest limits:
- LinkedIn blocks most non-browser requests to profile pages, so LinkedIn
  URLs will often come back with very little usable content — this is a
  LinkedIn restriction, not a bug here. GitHub profile/repo pages work well.
- This only reads whatever is publicly visible in the raw HTML — no login,
  no scraping behind auth walls, no bypassing anything.
"""

import re
import requests

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; GyrusAssistant/1.0)"}


def fetch_profile_text(url: str, max_chars: int = 4000) -> str:
    if not url.startswith("http"):
        url = "https://" + url
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        return f"__ERROR__: Could not fetch {url}: {e}"

    html = resp.text
    # crude tag strip — good enough for a summarization prompt, not meant to be a real scraper
    text = re.sub(r"<script.*?</script>", " ", html, flags=re.DOTALL)
    text = re.sub(r"<style.*?</style>", " ", text, flags=re.DOTALL)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:max_chars]


def analyze_profile(url: str, ask_fn) -> str:
    """ask_fn: e.g. brain.ask — kept as a parameter so this module has no
    direct dependency on which AI engine is configured."""
    content = fetch_profile_text(url)
    if content.startswith("__ERROR__"):
        return content.replace("__ERROR__: ", "")

    if len(content) < 200:
        return (f"Bahut kam content mila {url} se — agar ye LinkedIn hai, "
                f"LinkedIn zyada tar non-browser requests block kar deta hai, "
                f"is liye public data bohot limited milta hai. GitHub links behtar kaam karte hain.")

    prompt = (
        f"Here is the raw public text content of a profile page ({url}):\n\n{content}\n\n"
        "Summarize what this profile shows (skills, projects, focus areas), then give 3-4 "
        "specific, practical suggestions for what could be added or improved. Reply in Urdu+English mix."
    )
    return ask_fn(prompt)


if __name__ == "__main__":
    print(fetch_profile_text("https://github.com/Farhanillahiclass")[:500])
