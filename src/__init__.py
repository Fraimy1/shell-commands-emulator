from __future__ import annotations

import os
from pathlib import Path

_impl = os.getenv("APP_IMPL", "lab2").lower().strip()
_base = Path(__file__).resolve().parent

impl_dir = _base / "_impl_lab2" if "lab2" in _impl else (_base / f"_impl_{_impl}")

if not impl_dir.is_dir():
    raise ImportError(f"Unknown APP_IMPL={_impl!r}. Expected a folder like {impl_dir.name}")

__path__ = [str(impl_dir)]
