import json
import os
import requests

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT = os.getenv("TELEGRAM_CHAT_ID")
API = f"https://api.telegram.org/bot{TOKEN}"


def enabled():
    return bool(TOKEN and CHAT)


def send_message(text):
    if not enabled():
        print("[telegram disabled]", text[:80])
        return
    requests.post(f"{API}/sendMessage", data={"chat_id": CHAT, "text": text[:4000]}, timeout=30)


def send_photo(path, caption=""):
    if not enabled():
        return
    with open(path, "rb") as f:
        requests.post(f"{API}/sendPhoto", data={"chat_id": CHAT, "caption": caption[:1000]},
                      files={"photo": f}, timeout=60)


def skip_requested(since_ts):
    if not enabled():
        return False
    r = requests.get(f"{API}/getUpdates", params={
        "limit": 100, "allowed_updates": json.dumps(["message"])}, timeout=30)
    for u in r.json().get("result", []):
        m = u.get("message", {})
        if (str(m.get("chat", {}).get("id")) == str(CHAT)
                and m.get("date", 0) >= since_ts
                and m.get("text", "").strip().lower() in ("/skip", "skip")):
            return True
    return False
