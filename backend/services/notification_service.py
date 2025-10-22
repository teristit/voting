import requests
from config import Config

def send_notification(chat_id, message):
    if not Config.TELEGRAM_BOT_TOKEN:
        print("[notify] bot token not set")
        return False
    url = f"https://api.telegram.org/bot{Config.TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": message}
    try:
        r = requests.post(url, json=payload, timeout=5)
        return r.status_code == 200
    except Exception as e:
        print("[notify] error:", e)
        return False
