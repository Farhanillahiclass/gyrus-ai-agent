"""
email_manager.py — send emails and read/summarize unread inbox messages.
Uses Gmail (or any IMAP/SMTP provider) with an App Password — never your real
account password. Set EMAIL_ADDRESS / EMAIL_APP_PASSWORD in .env.
"""

import os
import imaplib
import smtplib
import email
from email.mime.text import MIMEText
from email.header import decode_header
from dotenv import load_dotenv

load_dotenv()

EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS", "")
EMAIL_APP_PASSWORD = os.getenv("EMAIL_APP_PASSWORD", "")
IMAP_SERVER = os.getenv("IMAP_SERVER", "imap.gmail.com")
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))


def send_email(to_address: str, subject: str, body: str):
    if not EMAIL_ADDRESS or not EMAIL_APP_PASSWORD:
        return "Email not configured — set EMAIL_ADDRESS and EMAIL_APP_PASSWORD in .env"
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = to_address

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_APP_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, [to_address], msg.as_string())
    return "sent"


def _decode(header_value):
    if not header_value:
        return ""
    parts = decode_header(header_value)
    return "".join(
        (p.decode(enc or "utf-8", errors="ignore") if isinstance(p, bytes) else p) for p, enc in parts
    )


def get_unread(limit: int = 5) -> list:
    """Returns a list of {from, subject, snippet} for the most recent unread emails."""
    if not EMAIL_ADDRESS or not EMAIL_APP_PASSWORD:
        return [{"error": "Email not configured — set EMAIL_ADDRESS and EMAIL_APP_PASSWORD in .env"}]

    results = []
    with imaplib.IMAP4_SSL(IMAP_SERVER) as mail:
        mail.login(EMAIL_ADDRESS, EMAIL_APP_PASSWORD)
        mail.select("inbox")
        status, data = mail.search(None, "UNSEEN")
        if status != "OK":
            return results
        ids = data[0].split()[-limit:]
        for eid in reversed(ids):
            status, msg_data = mail.fetch(eid, "(RFC822)")
            if status != "OK":
                continue
            msg = email.message_from_bytes(msg_data[0][1])
            subject = _decode(msg["Subject"])
            sender = _decode(msg["From"])
            snippet = ""
            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        try:
                            snippet = part.get_payload(decode=True).decode(errors="ignore")[:300]
                        except Exception:
                            pass
                        break
            else:
                try:
                    snippet = msg.get_payload(decode=True).decode(errors="ignore")[:300]
                except Exception:
                    pass
            results.append({"from": sender, "subject": subject, "snippet": snippet.strip()})
    return results


if __name__ == "__main__":
    for m in get_unread():
        print(m)
