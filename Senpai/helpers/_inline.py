from __future__ import annotations

from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from config import config
from Senpai.core.lang import get_string


def get_support_markup() -> InlineKeyboardMarkup | None:
    if config.SUPPORT_CHAT:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton(get_string("SUPPORT_BUTTON"), url=config.SUPPORT_CHAT)]
        ])
    return None
