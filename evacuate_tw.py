# File: monitor_travel_alert.py
import requests
from bs4 import BeautifulSoup
import json
import os
from datetime import datetime

LEVEL_URL = "https://travel.state.gov/content/travel/en/international-travel/International-Travel-Country-Information-Pages/Taiwan.html"
STATE_FILE = "last_level.json"

#TELEGRAM_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
#TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
TELEGRAM_TOKEN = "7997284138:AAErzBjG_4p3YNkhwNHdVmCIudLOfQ-jUX0"
TELEGRAM_CHAT_ID = "1626579522"


def fetch_alert_level() -> str:
    resp = requests.get(LEVEL_URL, timeout=10)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    level_tag_list = soup.find_all("h3", class_="tsg-rwd-eab-title-frame")
    if len(level_tag_list) >= 2:
        level_tag = level_tag_list[1]
    else:
        raise ValueError("Alert level element not found on the page.")

    return level_tag.text.strip()


def load_last_level() -> str:
    if not os.path.exists(STATE_FILE):
        return ""
    with open(STATE_FILE, "r") as f:
        data = json.load(f)
    return data.get("level", "")


def save_current_level(level: str):
    with open(STATE_FILE, "w") as f:
        json.dump({"level": level, "timestamp": datetime.now().isoformat()}, f)


def send_telegram_notify(msg: str):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram credentials not set in environment.")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": msg,
        "parse_mode": "Markdown"
    }
    r = requests.post(url, json=payload)
    r.raise_for_status()


def main():
    try:
        current_level = fetch_alert_level()
        previous_level = load_last_level()

        if current_level != previous_level:
            message = f"\U0001F6A8 *Travel Alert Update*\nTaiwan alert level changed!\n*Old:* {previous_level or 'N/A'}\n*New:* {current_level}"
            send_telegram_notify(message)
        else:
            print(f"No change in alert level: {current_level}")

        save_current_level(current_level)

    except Exception as e:
        send_telegram_notify(f"\u26A0\uFE0F *Error*: Travel Alert Monitor Failed\n{str(e)}")
        raise


if __name__ == "__main__":
    main()

