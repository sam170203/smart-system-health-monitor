import os
import smtplib
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.expanduser("~/.email_env"))

EMAIL = os.getenv("EMAIL_ADDRESS")
PASSWORD = os.getenv("EMAIL_PASSWORD")
TO_EMAIL = os.getenv("TO_EMAIL")

def send_alert(subject, body):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL
    msg["To"] = TO_EMAIL

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(EMAIL, PASSWORD)
            server.send_message(msg)
        print("✅ Email alert sent!")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
