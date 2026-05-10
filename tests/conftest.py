"""Pytest configuration: load `models.py` directly so unit tests don't
require Home Assistant to be installed."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

def _load(name: str, rel: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


wardragon_models = _load("wardragon_models", "custom_components/wardragon/models.py")
wardragon_const = _load("wardragon_const", "custom_components/wardragon/const.py")
