"""
social_post.py — prepares a post on LinkedIn/Twitter-X/Facebook by opening the
compose box and typing your text/image in for you.

Why this stops one click short of auto-publishing: LinkedIn, X, and Facebook's
Terms of Service explicitly prohibit automated/bot posting through anything
other than their official Developer APIs, and can suspend accounts that do it
via browser-automation bots. So Gyrus gets everything ready — you just glance
and hit Post. If you want *true* hands-free posting, register a developer app
with the platform (free) and use their official API instead; ask Gyrus's AI
brain for step-by-step help setting that up for whichever platform you pick.
"""

from playwright.sync_api import sync_playwright

COMPOSE_URLS = {
    "linkedin": "https://www.linkedin.com/feed/",
    "twitter": "https://twitter.com/compose/tweet",
    "facebook": "https://www.facebook.com/",
}


def prepare_post(platform: str, text: str, image_path: str = None):
    platform = platform.lower()
    if platform not in COMPOSE_URLS:
        print(f"Unsupported platform '{platform}'. Supported: {list(COMPOSE_URLS)}")
        return

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto(COMPOSE_URLS[platform])
        print(f"[social_post] Log in if needed, open the compose box, "
              f"then paste this text and attach the image yourself:\n\n{text}\n")
        if image_path:
            print(f"[social_post] Image to attach: {image_path}")
        page.wait_for_timeout(60_000)  # gives you a minute to log in / compose / post manually


if __name__ == "__main__":
    prepare_post("linkedin", "Excited to share my new project — Gyrus, a bilingual personal assistant!")
