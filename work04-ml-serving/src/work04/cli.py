from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def cmd_seed() -> int:
    root = Path(__file__).resolve().parents[2]
    subprocess.check_call([sys.executable, str(root / "scripts" / "seed_data.py")])
    return 0


def cmd_all() -> int:
    from work04.pipeline import run_all

    r = run_all()
    print("candidate pr_auc", r["candidate_test"]["pr_auc"])
    return 0


def cmd_test() -> int:
    root = Path(__file__).resolve().parents[2]
    return subprocess.call(
        [sys.executable, "-m", "pytest", "-q"],
        cwd=root,
        env={**dict(__import__("os").environ), "PYTHONPATH": str(root / "src")},
    )


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="work04")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("seed")
    sub.add_parser("all")
    sub.add_parser("test")
    sub.add_parser("lock", help="Зафіксувати config_hash у manifest")
    args = p.parse_args(argv)
    if args.cmd == "seed":
        return cmd_seed()
    if args.cmd == "all":
        return cmd_all()
    if args.cmd == "test":
        return cmd_test()
    if args.cmd == "lock":
        root = Path(__file__).resolve().parents[2]
        return subprocess.call([sys.executable, str(root / "scripts" / "lock_manifest.py")])
    return 1