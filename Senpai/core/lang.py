import json
from functools import wraps

from pyrogram import errors

from Senpai.core.dir import LOCALES_DIR
from Senpai.core.mongo import db

from loguru import logger

lang_codes = {
    "en": "English",
    "hi": "हिन्दी (Hindi)",
}

class Language:
    """
    Language class for managing multilingual support using JSON language files.
    """

    def __init__(self):
        self.lang_codes = lang_codes
        self.lang_dir = LOCALES_DIR
        self.languages = self.load_files()

    def load_files(self):
        languages = {}
        for lang_file in self.lang_dir.glob("*.json"):
            try:
                with open(lang_file, "r", encoding="utf-8") as file:
                    data = json.load(file)
                    lang_code = lang_file.stem
                    languages[lang_code] = data
                    
                    # Update lang_codes if specified in file
                    if "language_name" in data:
                        self.lang_codes[lang_code] = data["language_name"]
            except Exception as e:
                logger.error(f"Failed to load language file {lang_file.name}: {e}")
                
        logger.info(f"Loaded languages: {', '.join(languages.keys())}")
        return languages

    async def get_lang(self, chat_id: int) -> dict:
        lang_code = await db.get_chat_lang(chat_id)
        if lang_code not in self.languages:
            lang_code = "en"
        return self.languages[lang_code]

    def get_languages(self) -> dict:
        files = {f.stem for f in self.lang_dir.glob("*.json")}
        return {code: self.lang_codes.get(code, code) for code in sorted(files)}

    def language(self):
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                fallen = next(
                    (
                        arg
                        for arg in args
                        if hasattr(arg, "chat") or hasattr(arg, "message")
                    ),
                    None,
                )

                if fallen is None:
                    return await func(*args, **kwargs)

                if hasattr(fallen, "from_user") and fallen.from_user is None:
                    return

                if hasattr(fallen, "chat"):
                    chat = fallen.chat
                elif hasattr(fallen, "message"):
                    chat = fallen.message.chat
                else:
                    return await func(*args, **kwargs)

                if not chat:
                    return await func(*args, **kwargs)

                lang_code = await db.get_chat_lang(chat.id)
                if lang_code not in self.languages:
                    lang_code = "en"
                lang_dict = self.languages[lang_code]

                setattr(fallen, "lang", lang_dict)
                try:
                    return await func(*args, **kwargs)
                except (errors.ChannelPrivate, errors.MessageIdInvalid, errors.MessageNotModified):
                    return
                except (
                    errors.Forbidden,
                    errors.ChatWriteForbidden,
                ):
                    return

            return wrapper

        return decorator

lang = Language()
