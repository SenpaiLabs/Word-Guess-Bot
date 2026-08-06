from __future__ import annotations

import json
from functools import lru_cache

from Senpai.core.dir import LOCALES_DIR
from config import config


@lru_cache(maxsize=None)
def load_locale(lang: str = None) -> dict:
    lang = lang or config.DEFAULT_LANG
    path = LOCALES_DIR / f"{lang}.json"
    if not path.exists():
        path = LOCALES_DIR / "en.json"
    return json.loads(path.read_text(encoding="utf-8"))


def get_string(key: str, lang: str = None) -> str:
    lang = lang or config.DEFAULT_LANG
    return load_locale(lang).get(key, key)
