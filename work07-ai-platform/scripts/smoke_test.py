import json
import sys
import urllib.request

BASE = {
    "farm": "http://localhost:8081",
    "scout": "http://localhost:8082",
    "logistics": "http://localhost:8084",
    "rag": "http://localhost:8090",
}


def get(url: str) -> int:
    with urllib.request.urlopen(url, timeout=30) as r:
        return r.status


def post(url: str, payload: dict) -> dict:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())


def main() -> int:
    assert get(f"{BASE['farm']}/api/v1/fields") == 200
    assert get(f"{BASE['rag']}/health") == 200
    obs = post(f"{BASE['scout']}/api/v1/observations", {"fieldId": "F-001", "note": "бура іржа"})
    assert "observationId" in obs
    res = post(
        f"{BASE['logistics']}/api/v1/equipment-requests",
        {"fieldId": "F-001", "question": "норма висіву пшениці"},
    )
    hits = res.get("knowledgeHits", [])
    if not hits:
        print("FAIL: logistics returned no knowledge hits", file=sys.stderr)
        return 1
    print("OK smoke:", len(hits), "hits, top=", hits[0].get("docId") or hits[0].get("doc_id"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())