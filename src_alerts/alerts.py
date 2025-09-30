from __future__ import annotations
import os, json, smtplib
from email.mime.text import MIMEText
import requests
from dotenv import load_dotenv

load_dotenv()

SLACK = os.getenv("SLACK_WEBHOOK_URL")
DISCORD = os.getenv("DISCORD_WEBHOOK_URL")

def slack(msg: str):
    if not SLACK: return
    try:
        requests.post(SLACK, json={"text": msg}, timeout=10)
    except requests.RequestException:
        pass

def discord(msg: str):
    if not DISCORD: return
    try:
        requests.post(DISCORD, json={"content": msg}, timeout=10)
    except requests.RequestException:
        pass

def email(subject: str, body: str):
    host = os.getenv("EMAIL_SMTP_HOST")
    port = int(os.getenv("EMAIL_SMTP_PORT","587"))
    user = os.getenv("EMAIL_SMTP_USER")
    pwd  = os.getenv("EMAIL_SMTP_PASS")
    from_ = os.getenv("EMAIL_FROM")
    to_   = os.getenv("EMAIL_TO")
    if not all([host, user, pwd, from_, to_]): return
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject; msg["From"] = from_; msg["To"] = to_
    with smtplib.SMTP(host, port) as s:
        s.starttls(); s.login(user, pwd); s.sendmail(from_, [to_], msg.as_string())

def notify_all(subject: str, body: str):
    slack(f"*{subject}*\n{body}")
    discord(f"**{subject}**\n{body}")
    email(subject, body)
