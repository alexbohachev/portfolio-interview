"""p50/p95 для equipment-requests (slow vs fast). Стенд має бути піднятий."""
from __future__ import annotations

import json
import os
import statistics
import subprocess
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

LOGISTICS = os.getenv("LOGISTICS_URL", "http://localhost:8084").rstrip("/")
N = int(os.getenv("BENCH_N", "25"))
BODY = json.dumps({"fieldId": "F-001", "question": "бура іржа озимої пшениці фунгіцид"}).encode("utf-8")
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "artifacts" / "latency_before_after.json"
RAW = ROOT / "artifacts" / "latency_raw_samples.json"


def _git_sha() -> str | None:
    try:
        return (
            subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, text=True, stderr=subprocess.DEVNULL)
            .strip()
        )
    except Exception:
        return None


def call(profile: str) -> float:
    req = urllib.request.Request(
        f"{LOGISTICS}/api/v1/equipment-requests",
        data=BODY,
        headers={"Content-Type": "application/json", "X-Search-Profile": profile},
        method="POST",
    )
    t0 = time.perf_counter()
    with urllib.request.urlopen(req, timeout=180) as r:
        r.read()
    return time.perf_counter() - t0


def pctl(samples: list[float], q: float) -> float:
    if not samples:
        return 0.0
    xs = sorted(samples)
    pos = q * (len(xs) - 1)  # linear interpolation between ranks (same as numpy's default)
    lo = int(pos)
    hi = min(lo + 1, len(xs) - 1)
    return xs[lo] + (xs[hi] - xs[lo]) * (pos - lo)


def bench(profile: str) -> tuple[dict, list[float]]:
    times = [call(profile) for _ in range(N)]
    ms = [round(t * 1000, 2) for t in times]
    return (
        {
            "profile": profile,
            "n": N,
            "p50_ms": round(pctl(times, 0.5) * 1000, 1),
            "p95_ms": round(pctl(times, 0.95) * 1000, 1),
            "mean_ms": round(statistics.mean(times) * 1000, 1),
        },
        ms,
    )


def main() -> int:
    try:
        slow_stats, slow_ms = bench("slow")
        fast_stats, fast_ms = bench("fast")
    except OSError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    recorded = datetime.now(timezone.utc).isoformat()
    result = {
        "endpoint": "/api/v1/equipment-requests",
        "recorded_at_utc": recorded,
        "git_sha": _git_sha(),
        "bench_n": N,
        "slow": slow_stats,
        "fast": fast_stats,
        "speedup_p50": round(slow_stats["p50_ms"] / fast_stats["p50_ms"], 2) if fast_stats["p50_ms"] else None,
        "speedup_p95": round(slow_stats["p95_ms"] / fast_stats["p95_ms"], 2) if fast_stats["p95_ms"] else None,
        "jaeger_ui": os.getenv("JAEGER_UI", "http://localhost:16687"),
        "observability_note": "Trace logistics→rag-api: slow profile issues N+1 token calls; fast=single hybrid.",
    }
    raw = {
        "recorded_at_utc": recorded,
        "git_sha": _git_sha(),
        "slow_samples_ms": slow_ms,
        "fast_samples_ms": fast_ms,
        "request_body": json.loads(BODY.decode()),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    RAW.write_text(json.dumps(raw, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())