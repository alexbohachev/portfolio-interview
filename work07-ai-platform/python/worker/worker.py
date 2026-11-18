"""Worker: Kafka → rag-api index; scout → recommendation.ready; DLQ."""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

from kafka import KafkaConsumer, KafkaProducer

sys.path.insert(0, str(Path(__file__).resolve().parent))
from shared.recommendation import load_catalog, pick_actions  # noqa: E402

BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP", "localhost:9092")
TOPICS = [t.strip() for t in os.getenv("KAFKA_TOPICS", "document.uploaded,scout.report.created").split(",") if t.strip()]
RAG_API_URL = os.getenv("RAG_API_URL", "http://localhost:8090").rstrip("/")
RECOMMEND_TOPIC = os.getenv("KAFKA_TOPIC_RECOMMENDATION", "recommendation.ready")
DLQ_TOPIC = os.getenv("KAFKA_TOPIC_DLQ", "document.dlq")


def _post_json(url: str, payload: dict) -> dict:
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.loads(resp.read().decode())


def send_dlq(producer: KafkaProducer, raw: bytes, reason: str) -> None:
    payload = {"reason": reason, "raw_utf8": raw.decode("utf-8", errors="replace")[:4000]}
    producer.send(DLQ_TOPIC, json.dumps(payload, ensure_ascii=False).encode("utf-8"))


def index_via_rag(doc: dict) -> None:
    doc_id = doc.get("doc_id")
    if not doc_id:
        raise ValueError("missing doc_id")
    title = doc.get("title") or doc_id
    body = doc.get("body") or doc.get("note") or ""
    _post_json(f"{RAG_API_URL}/v1/admin/index", {"docId": doc_id, "title": title, "body": body})


def publish_recommendation(producer: KafkaProducer, doc: dict, actions: list[dict], mode: str) -> None:
    key = doc.get("correlation_id") or doc.get("doc_id") or "unknown"
    payload = {
        "event_id": doc.get("event_id"),
        "schema_version": 1,
        "correlation_id": key,
        "field_id": doc.get("field_id"),
        "observation_id": doc.get("correlation_id"),
        "actions": actions,
        "qa_mode": mode,
    }
    producer.send(RECOMMEND_TOPIC, json.dumps(payload, ensure_ascii=False).encode("utf-8"))


def maybe_recommend(producer: KafkaProducer, topic: str, doc: dict, catalog: list[dict]) -> None:
    if topic != "scout.report.created":
        return
    field_id = doc.get("field_id", "unknown")
    note = doc.get("body") or ""
    question = f"Рекомендації для поля {field_id}: {note}"
    search = _post_json(
        f"{RAG_API_URL}/v1/knowledge/search",
        {"query": question, "topK": 5, "mode": "hybrid"},
    )
    hits = search.get("hits") or []
    qa = _post_json(f"{RAG_API_URL}/v1/knowledge/qa", {"query": question, "topK": 5})
    mode = qa.get("mode", "extractive")
    actions = pick_actions(note, hits, catalog)
    publish_recommendation(producer, doc, actions, mode)


def main() -> None:
    catalog = load_catalog()
    producer = KafkaProducer(bootstrap_servers=BOOTSTRAP)
    consumer = KafkaConsumer(
        *TOPICS,
        bootstrap_servers=BOOTSTRAP,
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        consumer_timeout_ms=1000,
    )
    while True:
        polled = False
        for msg in consumer:
            polled = True
            raw = msg.value
            if not isinstance(raw, (bytes, bytearray)):
                raw = raw.encode("utf-8") if isinstance(raw, str) else bytes(raw)
            try:
                doc = json.loads(raw.decode("utf-8"))
            except (json.JSONDecodeError, UnicodeDecodeError):
                send_dlq(producer, raw, "json_decode")
                continue
            if not doc.get("doc_id"):
                send_dlq(producer, raw, "missing_doc_id")
                continue
            try:
                index_via_rag(doc)
                maybe_recommend(producer, msg.topic, doc, catalog)
            except (urllib.error.URLError, TimeoutError, ValueError) as exc:
                print(f"index error topic={msg.topic} doc={doc.get('doc_id')}: {exc}")
        if not polled:
            time.sleep(2)


if __name__ == "__main__":
    main()