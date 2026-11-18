from __future__ import annotations

import yaml

from work04.paths import CONFIG


def load_config():
    with CONFIG.open(encoding="utf-8") as f:
        return yaml.safe_load(f)