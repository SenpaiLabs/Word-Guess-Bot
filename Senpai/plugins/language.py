from pyrogram import filters, types, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from Senpai import app
from Senpai.core.lang import get_string
from Senpai.core.mongo import db
from Senpai.core.dir import LOCALES_DIR

import json

def get_available_languages() -> list[tuple[str, str]]:
    languages = []
    for file in LOCALES_DIR.glob("*.json"):
        try:
            data = json.loads(file.read_text(encoding="utf-8"))
            lang_code = file.stem
            lang_name = data.get("language_name", lang_code.upper())
            languages.append((lang_code, lang_name))
        except Exception:
            pass
    return languages

@app.on_callback_query(filters.regex("^lang$"))
async def language_menu_cb(_, query: types.CallbackQuery):
    chat_id = query.message.chat.id
    languages = get_available_languages()
    
    buttons = []
    for lang_code, lang_name in languages:
        buttons.append([InlineKeyboardButton(lang_name, callback_data=f"setlang_{lang_code}")])
    
    markup = InlineKeyboardMarkup(buttons)
    text = "Please select your preferred language:"
    
    await query.message.edit_text(text, reply_markup=markup)

@app.on_callback_query(filters.regex(r"^setlang_(.*)$"))
async def set_language_cb(_, query: types.CallbackQuery):
    lang_code = query.matches[0].group(1)
    chat_id = query.message.chat.id
    
    if chat_id < 0:
        # Check if user is admin in group
        user_id = query.from_user.id
        member = await app.get_chat_member(chat_id, user_id)
        if member.status not in (enums.ChatMemberStatus.ADMINISTRATOR, enums.ChatMemberStatus.OWNER):
            await query.answer("Only admins can change the group language!", show_alert=True)
            return

    await db.set_chat_lang(chat_id, lang_code)
    
    # Reload string in new language
    success_text = f"✅ Language successfully set to **{lang_code.upper()}** for this chat."
    
    await query.message.edit_text(success_text)
    await query.answer("Language updated successfully!", show_alert=True)
