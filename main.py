import datetime
import json
import sys
import time
from pathlib import Path

import config
import imagegen
import linkedin
import research
import tg
import writer

DATA = Path(__file__).parent / "data"
HISTORY = DATA / "history.json"
PENDING = DATA / "pending.json"
PENDING_IMG = DATA / "pending.png"


def now():
    return datetime.datetime.now(config.IST)


def load_history():
    return json.loads(HISTORY.read_text()) if HISTORY.exists() else []


def save_history(h):
    HISTORY.write_text(json.dumps(h[-200:], indent=2, ensure_ascii=False))


def generate():
    history = load_history()
    items = research.fetch_items(history)
    if not items:
        tg.send_message("No fresh research items found today. Nothing drafted.")
        return
    draft = writer.write_post(items, [h.get("title", "") for h in history[-30:]], now())
    imagegen.make_card(draft, PENDING_IMG)
    item = draft.get("item") or {}
    PENDING.write_text(json.dumps({
        "created": time.time(),
        "date": now().strftime("%Y-%m-%d"),
        "post": draft["post"],
        "headline": draft["headline"],
        "alt": draft.get("alt_text", draft["headline"]),
        "link": item.get("link"),
        "title": item.get("title") or draft["headline"],
    }, indent=2, ensure_ascii=False))
    tg.send_photo(PENDING_IMG, f"Draft for {now():%d %b %Y} ({draft['format']})")
    tg.send_message(draft["post"])
    if config.MODE == "auto":
        publish(force=True)
    else:
        tg.send_message("This will be posted at the scheduled time. Reply /skip to cancel it.")


def publish(force=False):
    if not PENDING.exists():
        print("No pending draft.")
        return
    p = json.loads(PENDING.read_text())
    history = load_history()
    if not force and tg.skip_requested(p["created"]):
        history.append({"date": p["date"], "link": p["link"], "title": p["title"], "status": "skipped"})
        save_history(history)
        PENDING.unlink()
        PENDING_IMG.unlink(missing_ok=True)
        tg.send_message("Skipped. Nothing was posted today.")
        return
    try:
        urn = linkedin.publish(p["post"], PENDING_IMG, p["headline"], p["alt"])
        if p.get("link"):
            try:
                linkedin.comment(urn, f"Source: {p['link']}")
            except Exception as e:
                print(f"[comment] failed: {e}")
    except Exception as e:
        tg.send_message(f"LinkedIn posting FAILED: {e}")
        raise
    history.append({"date": p["date"], "link": p["link"], "title": p["title"], "status": "posted"})
    save_history(history)
    PENDING.unlink()
    PENDING_IMG.unlink(missing_ok=True)
    tg.send_message("Posted to LinkedIn successfully.")


if __name__ == "__main__":
    action = sys.argv[1] if len(sys.argv) > 1 else "generate"
    if action == "generate":
        generate()
    elif action == "publish":
        publish()
    elif action == "both":
        generate()
        if config.MODE != "auto":
            publish()
    else:
        sys.exit("usage: main.py [generate|publish|both]")
