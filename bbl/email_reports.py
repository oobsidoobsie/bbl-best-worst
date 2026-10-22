"""Email only the two mobile-friendly Top 10 report images.

Configuration is stored in a local email_config.txt (git-ignored) and the SMTP
password/app password in email_secret.txt (also git-ignored). No credentials
are read from the repository's tracked files or passed on the command line.
"""
from __future__ import annotations

import os
import smtplib
import ssl
from email.message import EmailMessage
from pathlib import Path


IMAGE_NAMES = (
    "Top 10 Best - Mobile Friendly.png",
    "Top 10 Worst - Mobile Friendly.png",
)


def _read_key_values(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    with path.open("r", encoding="utf-8-sig") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            values[key.strip().lower()] = value.strip()
    return values


def _read_secret(path: Path) -> str:
    if not path.is_file():
        return ""
    with path.open("r", encoding="utf-8-sig") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if line and not line.startswith("#"):
                return line
    return ""


def send_top10_email(root: str, output_dir: str, label: str, say) -> bool:
    """Send exactly the two Top 10 mobile PNGs if local email is explicitly enabled."""
    root_path = Path(root)
    config_path = root_path / "email_config.txt"
    if not config_path.is_file():
        say("Email: not configured; copy email_config.example.txt to email_config.txt to enable.")
        return False

    cfg = _read_key_values(config_path)
    if cfg.get("enabled", "no").lower() not in {"yes", "true", "1"}:
        return False

    to_addresses = [item.strip() for item in cfg.get("to_email", "").replace(";", ",").split(",") if item.strip()]
    username = cfg.get("smtp_username", "")
    sender = cfg.get("from_email", "") or username
    host = cfg.get("smtp_host", "")
    try:
        port = int(cfg.get("smtp_port", "587"))
    except ValueError:
        say("Email failed: smtp_port must be a number in email_config.txt.")
        return False

    password = _read_secret(root_path / "email_secret.txt")
    if not to_addresses or not sender or not host or not (1 <= port <= 65535):
        say("Email failed: set to_email, from_email (or smtp_username), smtp_host and a valid smtp_port in email_config.txt.")
        return False
    if username and not password:
        say("Email failed: email_secret.txt is missing or empty.")
        return False

    out_path = Path(output_dir)
    image_paths = [out_path / name for name in IMAGE_NAMES]
    missing = [path.name for path in image_paths if not path.is_file()]
    if missing:
        say("Email skipped: both mobile-friendly images are required; missing " + ", ".join(missing))
        return False

    message = EmailMessage()
    message["Subject"] = f"{cfg.get('subject_prefix', 'BBL Best & Worst')} - {label}"
    message["From"] = sender
    message["To"] = ", ".join(to_addresses)
    message.set_content(
        f"Here are the two BBL Best & Worst mobile-friendly reports for {label}.\n\n"
        "Attached are Top 10 Best and Top 10 Worst.\n"
    )
    for path in image_paths:
        message.add_attachment(path.read_bytes(), maintype="image", subtype="png", filename=path.name)

    timeout = 30
    try:
        if cfg.get("smtp_ssl", "no").lower() in {"yes", "true", "1"}:
            with smtplib.SMTP_SSL(host, port, timeout=timeout, context=ssl.create_default_context()) as smtp:
                if username:
                    smtp.login(username, password)
                smtp.send_message(message)
        else:
            with smtplib.SMTP(host, port, timeout=timeout) as smtp:
                smtp.ehlo()
                smtp.starttls(context=ssl.create_default_context())
                smtp.ehlo()
                if username:
                    smtp.login(username, password)
                smtp.send_message(message)
    except (OSError, smtplib.SMTPException) as exc:
        # The email error is reported without displaying configured credentials.
        say(f"Email failed: {type(exc).__name__}: {str(exc)[:240]}")
        return False

    say(f"✅ Email sent to {', '.join(to_addresses)} with exactly two PNG attachments.")
    return True
