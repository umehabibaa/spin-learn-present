import random
import re
from functools import lru_cache
from pathlib import Path
from urllib.parse import quote

import httpx
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

BASE = Path(__file__).parent
STATIC = BASE.parent / "static"

CATEGORIES = [
    "Psychology & Human Behavior", "Weird Science", "Strange Things Happening on Earth",
    "Human Body", "History's Weirdest Stories", "Technology & Internet",
    "Philosophy & Thought Experiments", "Animals & Nature",
    "“Wait, That's Actually Real?” Topics", "Culture & Everyday Life",
]


def load_topics() -> list[dict]:
    """Parse topics.txt: category header lines, then one topic per line ('Title — hint')."""
    topics, seen, category = [], set(), "General"
    for raw in (BASE / "topics.txt").read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line:
            continue
        clean = re.sub(r"^[^\w“\"']+", "", line)  # strip leading emoji
        if clean in CATEGORIES:
            category = clean
            continue
        title, _, hint = line.partition(" — ")
        if title.lower() in seen:
            continue
        seen.add(title.lower())
        topics.append({"id": len(topics), "title": title.strip(),
                       "hint": hint.strip(), "category": category})
    return topics


TOPICS = load_topics()
app = FastAPI(title="Topic Spinner")


@app.get("/health")
def health():
    return {"ok": True, "topics": len(TOPICS)}


@app.get("/api/topics")
def all_topics():
    return TOPICS


@app.get("/api/topics/random")
def random_topic():
    return random.choice(TOPICS)


@app.get("/api/topics/{topic_id}")
def get_topic(topic_id: int):
    if not 0 <= topic_id < len(TOPICS):
        raise HTTPException(404, "Topic not found")
    return TOPICS[topic_id]


@lru_cache(maxsize=512)
def _wiki(title: str) -> dict | None:
    """Best-effort Wikipedia summary. Cached; returns None on any failure."""
    try:
        with httpx.Client(timeout=5, headers={"User-Agent": "topic-spinner-hobby/1.0"}) as c:
            s = c.get("https://en.wikipedia.org/w/rest.php/v1/search/page",
                      params={"q": title, "limit": 1}).json()
            if not s.get("pages"):
                return None
            key = s["pages"][0]["key"]
            r = c.get(f"https://en.wikipedia.org/api/rest_v1/page/summary/{quote(key)}").json()
            if not r.get("extract"):
                return None
            return {"title": r["title"], "extract": r["extract"],
                    "url": r["content_urls"]["desktop"]["page"]}
    except Exception:
        return None


@app.get("/api/topics/{topic_id}/summary")
def summary(topic_id: int):
    t = get_topic(topic_id)
    q = quote(t["title"])
    return {
        "wiki": _wiki(t["title"]),
        "links": [
            {"label": "Wikipedia", "url": f"https://en.wikipedia.org/w/index.php?search={q}"},
            {"label": "YouTube", "url": f"https://www.youtube.com/results?search_query={q}"},
            {"label": "Google", "url": f"https://www.google.com/search?q={q}"},
        ],
    }


@app.get("/")
def index():
    return FileResponse(STATIC / "index.html")


app.mount("/static", StaticFiles(directory=STATIC), name="static")
