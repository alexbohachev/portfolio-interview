from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def _ensure_src_path() -> None:
    root = Path(__file__).resolve().parents[2]
    src = root / "src"
    if str(src) not in sys.path:
        sys.path.insert(0, str(src))


def cmd_data() -> int:
    _ensure_src_path()
    from work01.config import load_config
    from work01.data import load_dataset
    from work01.paths import CONFIG_PATH, DATA_RAW

    cfg = load_config(CONFIG_PATH)
    _, meta = load_dataset(cfg, DATA_RAW)
    print(f"OK: {meta['n_rows']} rows, sha256={meta['zip_sha256']}")
    return 0


def cmd_all() -> int:
    _ensure_src_path()
    from work01.pipeline import run_all

    results = run_all()
    print("baseline test:", results["baseline_test"])
    print("candidate test:", results["candidate_test"])
    print(f"REPORT.md written ({results['elapsed_sec']}s)")
    return 0


def cmd_test() -> int:
    root = Path(__file__).resolve().parents[2]
    return subprocess.call([sys.executable, "-m", "pytest", "-q"], cwd=root)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="work01")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("data", help="Завантажити та перевірити дані")
    sub.add_parser("all", help="Повний цикл: baseline, candidate, звіт")
    sub.add_parser("test", help="Швидкі offline-тести (pytest)")
    args = parser.parse_args(argv)
    if args.command == "data":
        return cmd_data()
    if args.command == "all":
        return cmd_all()
    if args.command == "test":
        return cmd_test()
    return 1