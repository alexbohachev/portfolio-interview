from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def _src() -> None:
    root = Path(__file__).resolve().parents[2]
    p = root / "src"
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))


def cmd_seed() -> int:
    root = Path(__file__).resolve().parents[2]
    subprocess.check_call([sys.executable, str(root / "scripts" / "seed_corpus.py")])
    subprocess.check_call([sys.executable, str(root / "scripts" / "seed_golden.py")], env={**dict(__import__("os").environ), "PYTHONPATH": str(root / "src")})
    return 0


def cmd_all() -> int:
    _src()
    from work02.pipeline import run_all

    r = run_all()
    print("test recall@5 baseline", r["baseline"]["test"]["recall_at_k"])
    print("test recall@5 candidate", r["candidate"]["test"]["recall_at_k"])
    return 0


def cmd_test() -> int:
    root = Path(__file__).resolve().parents[2]
    return subprocess.call([sys.executable, "-m", "pytest", "-q"], cwd=root, env={**dict(__import__("os").environ), "PYTHONPATH": str(root / "src")})


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="work02")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("seed", help="Корпус + golden (MVP)")
    sub.add_parser("all", help="Індексування та оцінка retrieval")
    sub.add_parser("test")
    args = p.parse_args(argv)
    if args.cmd == "seed":
        return cmd_seed()
    if args.cmd == "all":
        return cmd_all()
    if args.cmd == "test":
        return cmd_test()
    return 1