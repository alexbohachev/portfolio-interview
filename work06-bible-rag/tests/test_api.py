from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from work06.app_main import app

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "artifacts" / "faiss.index"


@pytest.fixture
def client():
    return TestClient(app)


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


@pytest.mark.skipif(not INDEX.is_file(), reason="run make.ps1 index")
def test_ask_returns_citations(client):
    r = client.post(
        "/v1/ask",
        json={"question": "Що говорить вірш Gen.1.1 про творіння?", "top_k": 3, "use_llm": False},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["mode"] == "extractive"
    assert body["citations"]
    assert body["citations"][0]["osis_id"].startswith("Gen.1.")