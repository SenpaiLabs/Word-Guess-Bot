from __future__ import annotations

import json
from functools import lru_cache

from Senpai.core.dir import LOCALES_DIR


@lru_cache(maxsize=None)
def load_locale(lang: str = "en") -> dict:
    path = LOCALES_DIR / f"{lang}.json"
    if not path.exists():
        path = LOCALES_DIR / "en.json"
    return json.loads(path.read_text(encoding="utf-8"))


def get_string(key: str, lang: str = "en") -> str:
    if key == "SUPPORT_BUTTON":
        lookup = "support"
    else:
        lookup = key.lower()
    return load_locale(lang).get(lookup, key)
