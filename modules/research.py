"""
research.py — live info & research, using only FREE, no-signup APIs:
  - Weather: Open-Meteo (100% free, no key)
  - News: Google News RSS (free, no key)
  - Web search summary: DuckDuckGo HTML results (free, no key) + brain.ask() to summarize
  - Deep research: Wikipedia + Semantic Scholar (see note below) + AI synthesis into a saved article

Note on "Google Scholar": Google Scholar has no official API, and scraping
it directly breaks their Terms of Service and gets blocked (CAPTCHA) almost
immediately — it's not a reliable thing to build on. Semantic Scholar
(semanticscholar.org) is used instead: it's a free, official, legal API
covering a large slice of the same academic literature, run by the Allen
Institute for AI. Flagging the substitution rather than silently doing
something different from what was asked.
"""

import os
import re
import requests
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
CITY = os.getenv("CITY_FOR_WEATHER", "Islamabad")
RESEARCH_DIR = Path(__file__).resolve().parent.parent / "data" / "research"

WEATHER_CODES = {
    0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
    45: "Fog", 51: "Light drizzle", 61: "Light rain", 63: "Moderate rain",
    65: "Heavy rain", 71: "Snow", 80: "Rain showers", 95: "Thunderstorm",
}


def get_weather(city: str = None) -> str:
    city = city or CITY
    try:
        geo_resp = requests.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": city, "count": 1}, timeout=10
        )
        geo_resp.raise_for_status()
        geo = geo_resp.json()
    except (requests.exceptions.RequestException, ValueError) as e:
        return f"Weather service unreachable: {e}"
    if not geo.get("results"):
        return f"'{city}' نہیں ملا — city not found."
    loc = geo["results"][0]
    lat, lon = loc["latitude"], loc["longitude"]

    try:
        w_resp = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={"latitude": lat, "longitude": lon, "current_weather": True}, timeout=10
        )
        w_resp.raise_for_status()
        w = w_resp.json()
    except (requests.exceptions.RequestException, ValueError) as e:
        return f"Weather service unreachable: {e}"
    cw = w.get("current_weather", {})
    desc = WEATHER_CODES.get(cw.get("weathercode"), "Unknown")
    return f"{city}: {cw.get('temperature')}°C, {desc}, wind {cw.get('windspeed')} km/h"


def get_news(topic: str = "Pakistan", limit: int = 5) -> list:
    try:
        url = f"https://news.google.com/rss/search?q={requests.utils.quote(topic)}&hl=en-PK&gl=PK&ceid=PK:en"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        root = ET.fromstring(resp.content)
    except (requests.exceptions.RequestException, ET.ParseError) as e:
        return [{"title": f"News service unreachable: {e}", "link": ""}]
    items = root.findall(".//item")[:limit]
    return [{"title": i.findtext("title"), "link": i.findtext("link")} for i in items]


def web_search_summary(query: str, ask_fn=None) -> str:
    resp = requests.post(
        "https://html.duckduckgo.com/html/",
        data={"q": query},
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=10,
    )
    text = resp.text
    snippets = []
    marker = 'class="result__snippet"'
    idx = 0
    while True:
        idx = text.find(marker, idx)
        if idx == -1 or len(snippets) >= 5:
            break
        start = text.find(">", idx) + 1
        end = text.find("</a>", start)
        raw = text[start:end]
        clean = raw.replace("<b>", "").replace("</b>", "")
        snippets.append(clean)
        idx = end

    if not snippets:
        return "Koi result nahi mila — try rephrasing the query."

    combined = "\n".join(f"- {s}" for s in snippets)
    if ask_fn:
        return ask_fn(f"Summarize these search snippets about '{query}' in 3-4 clear sentences:\n{combined}")
    return combined


def wikipedia_summary(topic: str) -> dict:
    """Resolves `topic` to the best-matching Wikipedia article and returns
    its summary. Two real API calls: search (to resolve ambiguous topics),
    then the summary endpoint for the resolved title."""
    try:
        search = requests.get(
            "https://en.wikipedia.org/w/api.php",
            params={"action": "query", "list": "search", "srsearch": topic, "format": "json", "srlimit": 1},
            headers={"User-Agent": "GyrusAssistant/1.0"}, timeout=10,
        )
        search.raise_for_status()
        search_data = search.json()
    except (requests.exceptions.RequestException, ValueError) as e:
        return {"error": f"Wikipedia search failed: {e}"}

    hits = search_data.get("query", {}).get("search", [])
    if not hits:
        return {"error": f"Wikipedia par '{topic}' ke liye kuch nahi mila."}
    title = hits[0]["title"]

    try:
        resp = requests.get(
            f"https://en.wikipedia.org/api/rest_v1/page/summary/{requests.utils.quote(title)}",
            headers={"User-Agent": "GyrusAssistant/1.0"}, timeout=10,
        )
        resp.raise_for_status()
        summary = resp.json()
    except (requests.exceptions.RequestException, ValueError) as e:
        return {"error": f"Wikipedia summary fetch failed: {e}"}

    return {
        "title": summary.get("title", title),
        "extract": summary.get("extract", ""),
        "url": summary.get("content_urls", {}).get("desktop", {}).get("page", ""),
    }


def semantic_scholar_search(topic: str, limit: int = 5) -> list:
    """Real academic papers via Semantic Scholar's free public API — the
    legitimate substitute for Google Scholar (see module docstring)."""
    try:
        resp = requests.get(
            "https://api.semanticscholar.org/graph/v1/paper/search",
            params={"query": topic, "limit": limit, "fields": "title,abstract,year,authors,url"},
            timeout=15,
        )
        resp.raise_for_status()
        papers = resp.json().get("data", [])
    except (requests.exceptions.RequestException, ValueError) as e:
        return [{"error": f"Semantic Scholar request failed: {e}"}]

    return [{
        "title": p.get("title"),
        "year": p.get("year"),
        "authors": [a.get("name") for a in (p.get("authors") or [])][:4],
        "abstract": (p.get("abstract") or "")[:400],
        "url": p.get("url"),
    } for p in papers]


def _slugify(text: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", text.strip().lower()).strip("-")
    return slug[:60] or "research"


def deep_research(topic: str, ask_fn) -> dict:
    """
    The full research pipeline: Wikipedia summary + Semantic Scholar papers
    + a general web search, all handed to the AI brain to synthesize into a
    structured, well-organized article — then saved to disk as Markdown so
    it can be reopened, shared, or exported (e.g. to Word via the docx skill)
    any time, not just read once in chat.
    """
    wiki = wikipedia_summary(topic)
    papers = semantic_scholar_search(topic)
    web = web_search_summary(topic, ask_fn=None)  # raw snippets, not yet summarized

    sources_text = f"WIKIPEDIA:\n{wiki.get('extract', wiki.get('error',''))}\n\n"
    if papers and "error" not in papers[0]:
        sources_text += "ACADEMIC PAPERS (Semantic Scholar):\n"
        for p in papers:
            sources_text += f"- {p['title']} ({p['year']}) — {', '.join(p['authors'])}: {p['abstract'][:200]}\n"
    sources_text += f"\nWEB SEARCH SNIPPETS:\n{web}\n"

    prompt = (
        f"Using ONLY the source material below, write a well-organized research article about "
        f"'{topic}'. Structure it with a title, a short introduction, 3-5 clearly headed sections "
        f"covering the key aspects, and a brief conclusion. Write in clear English (this is for a "
        f"saved document). Cite sources inline as (Wikipedia) or (Semantic Scholar) where relevant.\n\n"
        f"SOURCE MATERIAL:\n{sources_text}"
    )
    article = ask_fn(prompt)

    RESEARCH_DIR.mkdir(parents=True, exist_ok=True)
    filename = f"{_slugify(topic)}-{datetime.now().strftime('%Y%m%d')}.md"
    filepath = RESEARCH_DIR / filename
    filepath.write_text(f"# {topic}\n\n{article}\n\n---\n*Generated by Gyrus, {datetime.now().strftime('%d %b %Y')}*\n", encoding="utf-8")

    return {"topic": topic, "article": article, "file_path": str(filepath), "filename": filename,
             "wikipedia_url": wiki.get("url", ""), "paper_count": len(papers) if papers and "error" not in papers[0] else 0}


if __name__ == "__main__":
    print(get_weather())
    print(get_news("technology"))
