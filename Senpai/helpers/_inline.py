from __future__ import annotations

from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from config import config
from Senpai.core.lang import get_string


def get_support_markup(chat_id: int) -> InlineKeyboardMarkup | None:
    if config.SUPPORT_CHAT:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton(get_string(chat_id, "support"), url=config.SUPPORT_CHAT)]
        ])
    return None

def start_pm_markup(bot_username: str, chat_id: int) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(get_string(chat_id, "add_me"), url=f"http://t.me/{bot_username}?startgroup=true")]
    ]
    
    row2 = []
    row2.append(InlineKeyboardButton(get_string(chat_id, "help"), callback_data="help"))
    if config.SUPPORT_CHAT:
        row2.append(InlineKeyboardButton(get_string(chat_id, "support"), url=config.SUPPORT_CHAT))
    if row2:
        buttons.append(row2)
        
    row3 = []
    if getattr(config, "SUPPORT_CHANNEL", ""):
        row3.append(InlineKeyboardButton(get_string(chat_id, "channel"), url=config.SUPPORT_CHANNEL))
    row3.append(InlineKeyboardButton(get_string(chat_id, "source"), url="https://github.com/SenpaiLabs/Word-Guess-Bot"))
    if row3:
        buttons.append(row3)
        
    return InlineKeyboardMarkup(buttons)

def start_gc_markup(chat_id: int) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(get_string(chat_id, "language"), callback_data="lang")]
    ]
    buttons[0].append(InlineKeyboardButton(get_string(chat_id, "source"), url="https://github.com/SenpaiLabs/Word-Guess-Bot"))
    
    return InlineKeyboardMarkup(buttons)
