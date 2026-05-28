from __future__ import annotations

import json
from pathlib import Path
from typing import Mapping


class I18n:
    def __init__(self, locales_dir: str, default_lang: str = "en"):
        self._default = default_lang
        self._catalog: dict[str, Mapping[str, str]] = {}
        for p in Path(locales_dir).glob("*.json"):
            with open(p, "r", encoding="utf-8") as f:
                self._catalog[p.stem] = json.load(f)

    def t(self, key: str, lang: str | None) -> str:
        lang = lang or self._default
        return (
                self._catalog.get(lang, {}).get(key)
                or self._catalog.get(self._default, {}).get(key)
                or key
        )
