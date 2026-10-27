"""Edit this file to customise your pipeline."""
import os
import datetime
from urllib.parse import quote

# ---- Branding (shown on the image footer) ----
BRAND_NAME = "Aravind | Technical Trainer"
BRAND_TAGLINE = "Follow for daily tech and career tips"

# ---- Audience (used in the writing prompt) ----
AUDIENCE = (
    "students, freshers and working developers in India who want to learn "
    "software skills, AI tools and get IT jobs"
)

# ---- Behaviour ----
# "review": draft goes to Telegram at generate time, posts at publish time unless you send /skip
# "auto"  : generate and post immediately
MODE = os.getenv("POST_MODE", "review").strip().lower()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
IST = datetime.timezone(datetime.timedelta(hours=5, minutes=30))
MAX_ITEM_AGE_DAYS = 3

# ---- Image look ----
IMAGE_STYLE = (
    "minimal futuristic technology illustration, abstract, dark blue palette, "
    "soft glow, no text, no letters, no logos"
)
PALETTES = [((15, 23, 42), (30, 64, 175)), ((17, 24, 39), (88, 28, 135)), ((6, 40, 50), (14, 116, 144))]
ACCENT = (250, 204, 21)


def gnews(q):
    return f"https://news.google.com/rss/search?q={quote(q)}&hl=en-IN&gl=IN&ceid=IN:en"


FEEDS = [
    ("Hacker News", "https://hnrss.org/frontpage?points=150"),
    ("dev.to", "https://dev.to/feed"),
    ("freeCodeCamp", "https://www.freecodecamp.org/news/rss/"),
    ("Stack Overflow Blog", "https://stackoverflow.blog/feed/"),
    ("GitHub Blog", "https://github.blog/feed/"),
    ("TechCrunch", "https://techcrunch.com/feed/"),
    ("The Verge", "https://www.theverge.com/rss/index.xml"),
    ("News: IT jobs India", gnews("IT jobs freshers hiring India")),
    ("News: AI developer tools", gnews("AI coding tools developers")),
    ("News: upskilling", gnews("software training upskilling India")),
]
