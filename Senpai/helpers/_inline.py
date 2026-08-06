from __future__ import annotations

from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from config import config
from Senpai.core.lang import get_string


def get_support_markup() -> InlineKeyboardMarkup | None:
    if config.SUPPORT_CHAT:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton(get_string("support"), url=config.SUPPORT_CHAT)]
        ])
    return None

def start_pm_markup(bot_username: str) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(get_string("btn_add_me"), url=f"http://t.me/{bot_username}?startgroup=true")]
    ]
    
    row2 = []
    row2.append(InlineKeyboardButton(get_string("btn_help"), callback_data="help"))
    if config.SUPPORT_CHAT:
        row2.append(InlineKeyboardButton(get_string("support"), url=config.SUPPORT_CHAT))
    if row2:
        buttons.append(row2)
        
    row3 = []
    if getattr(config, "CHANNEL_LINK", ""):
        row3.append(InlineKeyboardButton(get_string("btn_channel"), url=config.CHANNEL_LINK))
    if getattr(config, "SOURCE_LINK", ""):
        row3.append(InlineKeyboardButton(get_string("btn_source"), url=config.SOURCE_LINK))
    if row3:
        buttons.append(row3)
        
    return InlineKeyboardMarkup(buttons)

def start_gc_markup() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(get_string("btn_language"), callback_data="lang")]
    ]
    if getattr(config, "SOURCE_LINK", ""):
        buttons[0].append(InlineKeyboardButton(get_string("btn_source"), url=config.SOURCE_LINK))
    
    return InlineKeyboardMarkup(buttons)
