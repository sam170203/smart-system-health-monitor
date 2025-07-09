import requests
import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    response = requests.post(url, data=data)
    if response.status_code != 200:
        print("❌ Failed to send Telegram alert:", response.text)
    else:
        print("✅ Telegram alert sent.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("⚠️ Usage: python3 telegram_alert.py 'Your alert message here'")
    else:
        msg = " ".join(sys.argv[1:])
        send_telegram_alert(msg)

