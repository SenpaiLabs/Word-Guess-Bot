from __future__ import annotations

import json
from functools import lru_cache

from Senpai.core.dir import LOCALES_DIR
from config import config


chat_lang_cache: dict[int, str] = {}

@lru_cache(maxsize=None)
def load_locale(lang: str = None) -> dict:
    lang = lang or config.DEFAULT_LANG
    path = LOCALES_DIR / f"{lang}.json"
    if not path.exists():
        path = LOCALES_DIR / "en.json"
    return json.loads(path.read_text(encoding="utf-8"))


def get_string(chat_id: int, key: str) -> str:
    lang = chat_lang_cache.get(chat_id, config.DEFAULT_LANG)
    return load_locale(lang).get(key, key)
