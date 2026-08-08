
from pyrogram import types, enums

from config import config
from Senpai.core.lang import lang


class Inline:
    @staticmethod
    def lang_markup(_lang: str) -> types.InlineKeyboardMarkup:
        langs = lang.get_languages()
        buttons = [
            types.InlineKeyboardButton(
                text=f"{name} ({code}) {'✅' if code == _lang else ''}",
                callback_data=f"language {code}",
            )
            for code, name in langs.items()
        ]
        rows = [buttons[i : i + 2] for i in range(0, len(buttons), 2)]
        return types.InlineKeyboardMarkup(rows)

    @staticmethod
    def support_markup(_lang: dict) -> types.InlineKeyboardMarkup | None:
        if config.SUPPORT_CHAT:
            return types.InlineKeyboardMarkup([
                [types.InlineKeyboardButton(text=_lang.get("support", "Support"), url=config.SUPPORT_CHAT)]
            ])
        return None

    @staticmethod
    def help_markup(_lang: dict, back: bool = False) -> types.InlineKeyboardMarkup:
        if back:
            rows = [
                [
                    types.InlineKeyboardButton(text=_lang.get("help_back", "Back"), callback_data="help back", style=enums.ButtonStyle.PRIMARY),
                    types.InlineKeyboardButton(text=_lang.get("help_close", "Close"), callback_data="help close", style=enums.ButtonStyle.DANGER),
                ]
            ]
        else:
            cbs = ["game", "stats", "admin"]
            buttons = [
                types.InlineKeyboardButton(text=_lang.get(f"help_{cb}", cb.capitalize()), callback_data=f"help {cb}", style=enums.ButtonStyle.PRIMARY)
                for cb in cbs
            ]
            rows = [buttons[i : i + 3] for i in range(0, len(buttons), 3)]
            rows.append([types.InlineKeyboardButton(text=_lang.get("help_close", "Close"), callback_data="help close", style=enums.ButtonStyle.DANGER)])

        return types.InlineKeyboardMarkup(rows)

    @staticmethod
    def start_key(_lang: dict, bot_username: str, private: bool = False) -> types.InlineKeyboardMarkup:
        rows = [
            [
                types.InlineKeyboardButton(
                    text=_lang.get("add_me", "Add Me to Group"),
                    url=f"https://t.me/{bot_username}?startgroup=true",
                    style=enums.ButtonStyle.SUCCESS
                )
            ],
        ]

        if private:
            rows.append([
                types.InlineKeyboardButton(text=_lang.get("help", "Help"), callback_data="help", style=enums.ButtonStyle.PRIMARY),
                types.InlineKeyboardButton(text=_lang.get("source", "Source Code"), url="https://github.com/SenpaiLabs/Word-Guess-Bot"),
            ])
        else:
            rows.append([
                types.InlineKeyboardButton(text=_lang.get("help", "Help"), url=f"https://t.me/{bot_username}?start=help", style=enums.ButtonStyle.PRIMARY),
                types.InlineKeyboardButton(text=_lang.get("language", "Language"), callback_data="lang", style=enums.ButtonStyle.PRIMARY),
            ])

        row3 = []
        if config.SUPPORT_CHANNEL:
            row3.append(types.InlineKeyboardButton(text=_lang.get("channel", "Channel"), url=config.SUPPORT_CHANNEL))
        if config.SUPPORT_CHAT:
            row3.append(types.InlineKeyboardButton(text=_lang.get("support", "Support"), url=config.SUPPORT_CHAT))
        if row3:
            rows.append(row3)

        return types.InlineKeyboardMarkup(rows)


inline = Inline()
