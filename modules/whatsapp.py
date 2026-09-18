"""
whatsapp.py — sends WhatsApp messages via WhatsApp Web automation (pywhatkit).

How it actually works: pywhatkit opens web.whatsapp.com in your browser (you must
already be logged in there, same as any WhatsApp Web session) and simulates
typing + Enter at a scheduled time. This is browser automation of your own
logged-in session — not an unofficial API, not account takeover, and it fully
respects normal WhatsApp rate limits.

Deliberately NOT included: a one-click "send to everyone" blaster. Bulk sending
loops below always require you to pass an explicit list and include a delay,
and main.py asks for confirmation before calling send_bulk with more than one
recipient — please keep that guard. Spammy bulk messaging can get numbers banned
and may violate WhatsApp's Terms of Service.
"""

import time


def send_now(phone_number: str, message: str, wait_seconds: int = 15):
    """phone_number must include country code, e.g. '+923001234567'."""
    import pywhatkit
    pywhatkit.sendwhatmsg_instantly(phone_number, message, wait_time=wait_seconds, tab_close=True)


def send_to_group(group_invite_id: str, message: str, wait_seconds: int = 15):
    """group_invite_id: the part after 'chat.whatsapp.com/' in your group invite link."""
    import pywhatkit
    pywhatkit.sendwhatmsg_to_group_instantly(group_invite_id, message, wait_time=wait_seconds, tab_close=True)


def send_bulk(recipients: list, message: str, delay_seconds: int = 25):
    """
    recipients: list of phone numbers OR group_invite_ids.
    Sends the same message to each, one at a time, with a real delay between
    sends (default 25s) so it behaves like a human sending messages, not a bot blast.
    Call this only after the user has explicitly confirmed the full recipient list out loud or in text.
    """
    results = []
    for r in recipients:
        try:
            if r.startswith("+"):
                send_now(r, message)
            else:
                send_to_group(r, message)
            results.append((r, "sent"))
        except Exception as e:
            results.append((r, f"failed: {e}"))
        time.sleep(delay_seconds)
    return results


def send_attachment(phone_number: str, file_path: str, caption: str = ""):
    """Sends an image via WhatsApp Web. For non-image files, open WhatsApp Web
    and attach manually — pywhatkit only supports image attachments reliably."""
    import pywhatkit
    pywhatkit.sendwhats_image(phone_number, file_path, caption=caption, tab_close=True)


if __name__ == "__main__":
    # Example only — do not run without editing the number below.
    print("Edit this file with a real +countrycode number before testing send_now().")
