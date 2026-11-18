"""p50/p95 для equipment-requests (slow vs fast). Стенд має бути піднятий."""
from __future__ import annotations

import json
import os
import statistics
import sys
import time
import urllib.request

LOGISTICS = os.getenv("LOGISTICS_URL", "http://localhost:8084").rstrip("/")
N = int(os.getenv("BENCH_N", "25"))
BODY = json.dumps({"fieldId": "F-001", "question": "бура іржа озимої пшениці фунгіцид"}).encode("utf-8")
OUT = os.path.join(os.path.dirname(__file__), "..", "artifacts", "latency_before_after.json")


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
    idx = int(q * (len(xs) - 1))
    return xs[idx]


def bench(profile: str) -> dict:
    times = [call(profile) for _ in range(N)]
    return {
        "profile": profile,
        "n": N,
        "p50_ms": round(pctl(times, 0.5) * 1000, 1),
        "p95_ms": round(pctl(times, 0.95) * 1000, 1),
        "mean_ms": round(statistics.mean(times) * 1000, 1),
    }


def main() -> int:
    try:
        slow = bench("slow")
        fast = bench("fast")
    except OSError as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    result = {
        "endpoint": "/api/v1/equipment-requests",
        "slow": slow,
        "fast": fast,
        "speedup_p50": round(slow["p50_ms"] / fast["p50_ms"], 2) if fast["p50_ms"] else None,
    }
    out_path = os.path.normpath(OUT)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())