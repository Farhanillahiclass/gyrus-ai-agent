"""
auto_login.py — fills in login forms on sites YOU already have accounts on.

Security approach (please don't change this):
  - Credentials are stored in your OS's secure credential vault via `keyring`
    (Windows Credential Manager / macOS Keychain / Linux Secret Service) —
    NEVER in a plaintext file, NEVER in this repo.
  - This only fills fields on a page you specify by CSS selector — it does not
    guess selectors on arbitrary sites, and it does not attempt to defeat CAPTCHAs,
    2FA, or bot-detection. Sites that require those are protecting themselves for
    good reasons; use their "remember me" feature or a real password manager instead.

One-time setup for a site:
    python -c "import keyring; keyring.set_password('gyrus', 'myuni_username', 'farhan123')"
    python -c "import keyring; keyring.set_password('gyrus', 'myuni_password', 'REAL_PASSWORD')"
"""

import keyring
from playwright.sync_api import sync_playwright


def autofill_login(url: str, username_selector: str, password_selector: str,
                    submit_selector: str, cred_key: str):
    """
    cred_key: the name you used when saving credentials with keyring, e.g. 'myuni'
    (looks up '{cred_key}_username' and '{cred_key}_password' in the OS vault).
    """
    username = keyring.get_password("gyrus", f"{cred_key}_username")
    password = keyring.get_password("gyrus", f"{cred_key}_password")
    if not username or not password:
        print(f"No stored credentials for '{cred_key}'. Save them first with keyring.set_password().")
        return

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # visible on purpose — you should see what's happening
        page = browser.new_page()
        page.goto(url)
        page.fill(username_selector, username)
        page.fill(password_selector, password)
        page.click(submit_selector)
        page.wait_for_timeout(3000)
        # Browser stays open so you can handle any 2FA prompt yourself.


if __name__ == "__main__":
    print("Configure a site-specific call to autofill_login() — see docstring for setup.")
