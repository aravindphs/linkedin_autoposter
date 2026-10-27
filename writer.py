import json
import os
from pathlib import Path
import requests
import config

DATA = Path(__file__).parent / "data"

FORMATS = {
    0: "Career tip for students and freshers",
    1: "IT industry news take: what happened and why it matters to learners",
    2: "Mini tutorial: one practical tip or idea people can try today (evergreen is fine)",
    3: "Myth vs fact about a technology or career path (evergreen is fine)",
    4: "Technology spotlight: what it is, who should learn it, how to start",
    5: "Learning roadmap or study strategy (evergreen is fine)",
    6: "Trainer reflection: a classroom lesson or motivation for learners (evergreen is fine)",
}


def _prompt(items, recent_titles, fmt):
    style = (DATA / "style.md").read_text()
    examples = (DATA / "examples.md").read_text()
    listing = "\n".join(
        f"[{i}] ({it['source']}) {it['title']} | {it['summary']}" for i, it in enumerate(items)
    )
    recent = "\n".join(f"- {t}" for t in recent_titles) or "- none"
    return (
        "You write one LinkedIn post per day for a technical trainer.\n"
        f"Audience: {config.AUDIENCE}.\n\n"
        f"TODAY'S FORMAT: {fmt}\n\n"
        f"STYLE GUIDE:\n{style}\n\nEXAMPLES OF THE TRAINER'S OWN POSTS:\n{examples}\n\n"
        f"RECENT TOPICS (do not repeat):\n{recent}\n\n"
        f"CANDIDATE NEWS ITEMS:\n{listing}\n\n"
        "TASK: Pick the ONE item most useful for the audience and fitting today's format, "
        "then write the post. If the format is evergreen and no item fits, set pick to -1. "
        "When you use an item, rely ONLY on facts in its title and summary; if unsure, stay general.\n\n"
        "Return ONLY JSON with these keys:\n"
        '{"pick": int, "tag": "2-3 word uppercase label like TECH TIP", '
        '"headline": "max 9 words for the image", '
        '"points": ["3 short takeaways, max 9 words each"], '
        '"post": "full LinkedIn post text including hashtags", '
        '"image_prompt": "one sentence describing an abstract illustration related to the topic, no text in image", '
        '"alt_text": "one sentence image description"}'
    )


def _call(prompt):
    key = os.environ["GEMINI_API_KEY"]
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{config.GEMINI_MODEL}:generateContent"
    body = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseMimeType": "application/json",
            "thinkingConfig": {"thinkingLevel": os.getenv("GEMINI_THINKING", "low")},
        },
    }
    r = requests.post(url, headers={"x-goog-api-key": key}, json=body, timeout=(15, 180))
    if r.status_code != 200:
        raise RuntimeError(f"Gemini error {r.status_code}: {r.text[:600]}")
    data = r.json()
    try:
        parts = data["candidates"][0]["content"]["parts"]
        text = "".join(p.get("text", "") for p in parts if not p.get("thought"))
    except (KeyError, IndexError):
        raise RuntimeError(f"Unexpected Gemini response: {str(data)[:600]}")
    return json.loads(text)


def write_post(items, recent_titles, now):
    fmt = FORMATS[now.weekday()]
    data = _call(_prompt(items, recent_titles, fmt))
    if isinstance(data, list):
        data = data[0]
    if len(data.get("post", "")) < 200 or len(data.get("points", [])) < 2:
        raise RuntimeError(f"Gemini returned an incomplete post: {str(data)[:400]}")
    pick = data.get("pick", -1)
    item = items[pick] if isinstance(pick, int) and 0 <= pick < len(items) else None
    data["post"] = data["post"].strip()[:2900]
    data["item"] = item
    data["format"] = fmt
    return data
