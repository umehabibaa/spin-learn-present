# Spin. Learn. Present.

A small web app for learning something new and practicing how you explain it.

1. **Spin** a slot-machine reel that lands on a random topic (Mandela effect, placebo effect, the Fermi paradox, and about 300 more).
2. **Learn** for 15 minutes, with a starter summary, search links, and a notes box.
3. **Present** to your camera for up to 5 minutes.
4. **Save** the video to your device, or skip. Nothing is uploaded.

Video is recorded in the browser with the `MediaRecorder` API and never reaches the server. There is no database.

## Stack

| Layer | Choice | Why |
|---|---|---|
| Backend | FastAPI (Python 3.12) | Serves topics, a cached Wikipedia summary, and the frontend |
| Frontend | Plain HTML, CSS, vanilla JS | Camera and recording only exist in the browser |
| Container | Docker (`python:3.12-slim`) | One image runs locally and in production |
| Tests | pytest | Covers topic parsing and the API |
| Hosting | Render (free web service) | Runs Docker images, free tier available |

## Project structure

    spin/
    ├── app/
    │   ├── main.py          # FastAPI app and topic parser
    │   └── topics.txt       # editable topic list
    ├── static/
    │   └── index.html       # whole frontend (strawberry matcha theme)
    ├── tests/test_api.py
    ├── Dockerfile
    ├── requirements.txt
    └── README.md

## API

| Endpoint | Returns |
|---|---|
| `GET /health` | `{"ok": true, "topics": <count>}` (used for health checks) |
| `GET /api/topics` | All topics: `id`, `title`, `hint`, `category` |
| `GET /api/topics/random` | One random topic |
| `GET /api/topics/{id}` | One topic, or 404 |
| `GET /api/topics/{id}/summary` | Wikipedia summary (best effort, cached) plus Wikipedia, YouTube and Google search links |
| `GET /docs` | Interactive API docs |

## Run locally (Python)

    python -m venv .venv
    .venv\Scripts\activate          # macOS/Linux: source .venv/bin/activate
    pip install -r requirements.txt
    uvicorn app.main:app --reload

Open http://localhost:8000.

Add `?fast=1` to the URL for 10-second timers while testing:
http://localhost:8000/?fast=1

## Run with Docker

    docker build -t spinner .
    docker run --rm -p 8000:7860 spinner

Open http://localhost:8000. Camera access works on `localhost` without HTTPS. The container listens on `$PORT`, defaulting to 7860.

## Tests

    pytest

## Deploy free on Render

Hugging Face Docker Spaces now require a PRO subscription for new accounts, so this project deploys on Render. Free-tier terms change, so check Render's current pricing page first.

1. Push this folder to a GitHub repo.
2. On Render: **New → Web Service**, connect the repo.
3. Language: **Docker**. Instance type: **Free**.
4. Set **Health Check Path** to `/health`.
5. Deploy, then open the `onrender.com` URL.
6. Test on your phone. Camera access needs HTTPS, which Render provides.

No code changes are needed, because the Dockerfile already reads the `PORT` variable that Render sets.

### The cold-start caveat

Free Render web services spin down after 15 minutes without traffic and take about a minute to wake. If you share the link publicly:

- Say in the post that the first load can take about a minute.
- Optional: ping `/health` every 14 minutes with UptimeRobot or a scheduled GitHub Action. This is a community workaround, not an officially supported feature.

## Editing topics

Open `app/topics.txt`. A line is either a category header or a topic:

    Weird Science
    The Mpemba Effect — hot water can freeze faster than cold under some conditions
    Dark Matter

- Text after ` — ` becomes the hint shown under the topic title.
- New category names must also be added to the `CATEGORIES` list in `app/main.py`, otherwise their topics are filed under the previous category.
- Duplicate titles are ignored.

## Known limitations

- The Wikipedia lookup takes the top search hit, so some topics get a loosely related summary or none. The search links are the fallback.
- Notes and timers live only in the page. Refreshing the tab loses them.
- Chrome records WebM and Safari records MP4. The code picks a supported format automatically, but Safari and mobile browsers are untested.
- Videos are recorded at 1.5 Mbps, so a full 5-minute clip is roughly 55 MB.

## Ideas for later

- GitHub Actions workflow that runs `pytest` on every push.
- Filler-word counting with the Web Speech API (Chrome only) and a "your talk" summary at the end.
- Category filter before spinning.
- A "history" of topics you've already done, stored in `localStorage`.
