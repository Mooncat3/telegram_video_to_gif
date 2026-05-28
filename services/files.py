from __future__ import annotations

from pathlib import Path

from config import settings

Path(settings.temp_dir).mkdir(parents=True, exist_ok=True)


def temp_path(*parts: str) -> str:
    p = Path(settings.temp_dir, *parts)
    p.parent.mkdir(parents=True, exist_ok=True)
    return str(p)
