import re
import time
import datetime
import feedparser
import config


def _clean(html):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", html or "")).strip()


def fetch_items(history, per_feed=5):
    seen = {h.get("link") for h in history}
    cutoff = time.time() - config.MAX_ITEM_AGE_DAYS * 86400
    items = []
    for source, url in config.FEEDS:
        try:
            feed = feedparser.parse(url, request_headers={"User-Agent": "Mozilla/5.0"})
        except Exception as e:
            print(f"[research] {source} failed: {e}")
            continue
        count = 0
        for e in feed.entries:
            link = e.get("link")
            if not link or link in seen:
                continue
            ts = e.get("published_parsed") or e.get("updated_parsed")
            if ts and time.mktime(ts) < cutoff:
                continue
            items.append({
                "source": source,
                "title": _clean(e.get("title"))[:200],
                "link": link,
                "summary": _clean(e.get("summary"))[:350],
            })
            count += 1
            if count >= per_feed:
                break
    print(f"[research] {len(items)} candidate items")
    return items[:40]
