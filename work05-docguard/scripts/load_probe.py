"""Легкий навантажувальний зонд ~1 RPS (звіт у stdout)."""
from __future__ import annotations

import argparse
import json
import time
import urllib.error
import urllib.request


def one_post(base: str, question: str) -> tuple[int, float]:
    body = json.dumps({"question": question}, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        f"{base.rstrip('/')}/api/v1/query",
        data=body,
        headers={
            "Content-Type": "application/json; charset=utf-8",
            "X-Tenant-Id": "tenant_a",
            "X-Principal-Id": "alice",
        },
        method="POST",
    )
    t0 = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            status = resp.status
    except urllib.error.HTTPError as e:
        status = e.code
    dt = (time.perf_counter() - t0) * 1000
    return status, dt


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--gateway", default="http://localhost:8096")
    p.add_argument("--duration-sec", type=int, default=60)
    p.add_argument("--rps", type=float, default=1.0)
    args = p.parse_args()
    interval = 1.0 / args.rps
    deadline = time.time() + args.duration_sec
    ok = 0
    lat: list[float] = []
    n = 0
    q = "бура іржа"
    while time.time() < deadline:
        n += 1
        status, ms = one_post(args.gateway, f"{q} #{n}")
        lat.append(ms)
        if 200 <= status < 300:
            ok += 1
        time.sleep(max(0, interval - 0.001))
    lat.sort()
    p50 = lat[len(lat) // 2] if lat else 0
    print(
        json.dumps(
            {
                "n": n,
                "ok": ok,
                "error_rate": round(1 - ok / n, 4) if n else 0,
                "latency_ms_p50": round(p50, 1),
            },
            ensure_ascii=False,
        )
    )
    return 0 if ok == n else 1


if __name__ == "__main__":
    raise SystemExit(main())