from __future__ import annotations

from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from config import config



def get_support_markup(lang_dict: dict) -> InlineKeyboardMarkup | None:
    if config.SUPPORT_CHAT:
        return InlineKeyboardMarkup([
            [InlineKeyboardButton(lang_dict.get("support", "Support"), url=config.SUPPORT_CHAT)]
        ])
    return None

def start_pm_markup(bot_username: str, lang_dict: dict) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(lang_dict.get("add_me", "Add Me to Group"), url=f"http://t.me/{bot_username}?startgroup=true")]
    ]
    
    row2 = []
    row2.append(InlineKeyboardButton(lang_dict.get("help", "Help"), callback_data="help"))
    if config.SUPPORT_CHAT:
        row2.append(InlineKeyboardButton(lang_dict.get("support", "Support"), url=config.SUPPORT_CHAT))
    if row2:
        buttons.append(row2)
        
    row3 = []
    if getattr(config, "SUPPORT_CHANNEL", ""):
        row3.append(InlineKeyboardButton(lang_dict.get("channel", "Channel"), url=config.SUPPORT_CHANNEL))
    row3.append(InlineKeyboardButton(lang_dict.get("source", "Source Code"), url="https://github.com/SenpaiLabs/Word-Guess-Bot"))
    if row3:
        buttons.append(row3)
        
    return InlineKeyboardMarkup(buttons)

def start_gc_markup(lang_dict: dict) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(lang_dict.get("language", "Language"), callback_data="lang")]
    ]
    buttons[0].append(InlineKeyboardButton(lang_dict.get("source", "Source Code"), url="https://github.com/SenpaiLabs/Word-Guess-Bot"))
    
    return InlineKeyboardMarkup(buttons)
