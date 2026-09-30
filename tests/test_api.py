from fastapi.testclient import TestClient
from app.main import app, TOPICS

c = TestClient(app)


def test_topics_parsed():
    titles = [t["title"].lower() for t in TOPICS]
    assert len(TOPICS) > 250
    assert len(titles) == len(set(titles))
    assert all(t["category"] != "General" for t in TOPICS)


def test_random_and_by_id():
    t = c.get("/api/topics/random").json()
    assert c.get(f"/api/topics/{t['id']}").json() == t
    assert c.get("/api/topics/99999").status_code == 404


def test_index_served():
    assert c.get("/").status_code == 200
