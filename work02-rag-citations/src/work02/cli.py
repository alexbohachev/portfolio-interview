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


def cmd_lock() -> int:
    _src()
    from work02.config import config_fingerprint, load_config
    from work02.paths import CONFIG, MANIFEST

    import json

    fp = config_fingerprint(load_config(CONFIG))
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    manifest["config_hash"] = fp
    manifest.pop("pending_lock", None)
    MANIFEST.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"config_hash={fp}")
    return 0


def cmd_all() -> int:
    _src()
    from work02.pipeline import run_all

    r = run_all()
    print("recall@5 baseline", r["baseline_retrieval_test"]["recall_at_k"])
    print("recall@5 hybrid", r["candidate_retrieval_test"]["recall_at_k"])
    print("qa", r["qa_test"])
    return 0


def cmd_test() -> int:
    root = Path(__file__).resolve().parents[2]
    return subprocess.call([sys.executable, "-m", "pytest", "-q"], cwd=root, env={**dict(__import__("os").environ), "PYTHONPATH": str(root / "src")})


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="work02")
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("lock", help="Зафіксувати config_hash у manifest")
    sub.add_parser("seed", help="Корпус 200 + golden dev/test")
    sub.add_parser("all", help="Індексування та оцінка retrieval")
    sub.add_parser("test")
    sub.add_parser("eval-llm", help="OpenAI judge на 30 dev (потрібен OPENAI_API_KEY)")
    args = p.parse_args(argv)
    if args.cmd == "lock":
        return cmd_lock()
    if args.cmd == "seed":
        return cmd_seed()
    if args.cmd == "all":
        return cmd_all()
    if args.cmd == "test":
        return cmd_test()
    if args.cmd == "eval-llm":
        root = Path(__file__).resolve().parents[2]
        return subprocess.call(
            [sys.executable, str(root / "scripts" / "eval_llm_judge.py")],
            cwd=root,
            env={**dict(__import__("os").environ), "PYTHONPATH": str(root / "src")},
        )
    return 1