from pyrogram import filters, types

from Senpai import app
from Senpai.core.lang import lang
from Senpai.core.mongo import db
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def lang_markup(current_lang: str):
    languages = lang.get_languages()
    buttons = []
    for lang_code, lang_name in languages.items():
        text = f"{lang_name} {'✅' if current_lang == lang_code else ''}"
        buttons.append([InlineKeyboardButton(text, callback_data=f"language {lang_code}")])
    return InlineKeyboardMarkup(buttons)

@app.on_message(filters.command(["lang", "language"]))
@lang.language()
async def _lang_cmd(_, m: types.Message):
    current = await db.get_chat_lang(m.chat.id)
    keyboard = lang_markup(current)
    await m.reply_text(m.lang.get("lang_choose", "Please select your preferred language:"), reply_markup=keyboard)


@app.on_callback_query(filters.regex(r"^language") | filters.regex(r"^lang$"))
@lang.language()
async def _lang_cb(_, query: types.CallbackQuery):
    data = query.data.split()
    
    chat_id = query.message.chat.id
    if chat_id < 0:
        # Check if user is admin in group
        user_id = query.from_user.id
        member = await app.get_chat_member(chat_id, user_id)
        if member.status not in (types.enums.ChatMemberStatus.ADMINISTRATOR, types.enums.ChatMemberStatus.OWNER):
            await query.answer(query.lang.get("lang_admin_only", "Only admins can change the group language!"), show_alert=True)
            return

    if data[0] in ["language", "lang"] and len(data) == 1:
        current = await db.get_chat_lang(chat_id)
        keyboard = lang_markup(current)
        return await query.edit_message_text(
            query.lang.get("lang_choose", "Please select your preferred language:"), reply_markup=keyboard
        )

    _lang_code = data[1]
    current = await db.get_chat_lang(chat_id)
    if current == _lang_code:
        return await query.answer(
            query.lang.get("lang_same", "Language is already {}!").format(current), show_alert=True
        )

    await db.set_chat_lang(chat_id, _lang_code)
    
    # Reload string in new language by fetching manually for the confirmation message
    lang_dict = lang.languages.get(_lang_code, lang.languages["en"])
    success_text = lang_dict.get("lang_changed", "✅ Language successfully set to **{}** for this chat.").format(_lang_code.upper())
    
    await query.answer(f"Language changed to {_lang_code.upper()}", show_alert=True)
    await query.edit_message_text(success_text)
