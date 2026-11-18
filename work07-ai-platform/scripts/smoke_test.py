import json
import sys
import urllib.request

BASE = {
    "farm": "http://localhost:8081",
    "scout": "http://localhost:8082",
    "logistics": "http://localhost:8084",
    "rag": "http://localhost:8090",
}


def get_json(url: str) -> dict:
    with urllib.request.urlopen(url, timeout=120) as r:
        return json.loads(r.read().decode())


def post(url: str, payload: dict) -> dict:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read().decode())


def main() -> int:
    with urllib.request.urlopen(f"{BASE['farm']}/api/v1/fields", timeout=30) as r:
        assert r.status == 200
    farm_doc = post(
        f"{BASE['farm']}/api/v1/documents",
        {"fieldId": "F-001", "title": "Нотатка поля", "body": "озима пшениця норма висіву"},
    )
    assert farm_doc.get("kafkaTopic") == "document.uploaded"
    health = get_json(f"{BASE['rag']}/health")
    if health.get("status") != "ok":
        print("FAIL: rag-api health", health, file=sys.stderr)
        return 1
    indexed = health.get("indexed_docs", 0)
    if indexed < 10:
        print("WARN: indexed_docs=", indexed)

    hybrid = post(f"{BASE['rag']}/v1/knowledge/search", {"query": "бура іржа пшениці", "topK": 5, "mode": "hybrid"})
    if not hybrid.get("hits"):
        print("FAIL: hybrid search empty", file=sys.stderr)
        return 1

    qa = post(f"{BASE['logistics']}/api/v1/knowledge/qa", {"question": "Критичний фактор для хвороб пшениці?"})
    if qa.get("refused"):
        print("FAIL: expected answer, got refusal", qa, file=sys.stderr)
        return 1
    if not qa.get("citations") and qa.get("mode") == "extractive":
        print("FAIL: missing citations", qa, file=sys.stderr)
        return 1

    obs = post(f"{BASE['scout']}/api/v1/observations", {"fieldId": "F-001", "note": "бура іржа"})
    assert "observationId" in obs
    assert obs.get("kafkaTopic") == "scout.report.created"
    res = post(
        f"{BASE['logistics']}/api/v1/equipment-requests",
        {"fieldId": "F-001", "question": "ІПМ шкідники"},
    )
    hits = res.get("knowledgeHits", [])
    if not hits:
        print("FAIL: logistics hybrid hits", file=sys.stderr)
        return 1
    slow_req = urllib.request.Request(
        f"{BASE['logistics']}/api/v1/equipment-requests",
        data=json.dumps({"fieldId": "F-001", "question": "бура іржа пшениці"}).encode(),
        headers={"Content-Type": "application/json", "X-Search-Profile": "slow"},
        method="POST",
    )
    with urllib.request.urlopen(slow_req, timeout=120) as r:
        slow_body = json.loads(r.read().decode())
    if not slow_body.get("knowledgeHits"):
        print("FAIL: slow profile empty", file=sys.stderr)
        return 1

    print(
        "OK smoke:",
        f"indexed={indexed}",
        f"hybrid_hits={len(hybrid['hits'])}",
        f"qa_mode={qa.get('mode')}",
        f"logistics_hits={len(hits)}",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())