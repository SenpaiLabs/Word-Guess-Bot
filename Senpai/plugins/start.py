from __future__ import annotations

from pyrogram import filters, types, enums

from Senpai.core.mongo import db
from Senpai import app
from Senpai.helpers._dataclass import User
from Senpai.core.lang import lang
from Senpai.helpers._inline import start_pm_markup, start_gc_markup
from config import config


@app.on_message(filters.command("start"))
@lang.language()
async def start_cmd(_, m: types.Message):
    if m.from_user:
        await db.register_user(User(user_id=m.from_user.id, first_name=m.from_user.first_name, username=m.from_user.username))
        
        if config.LOG_GROUP_ID and m.chat.type == enums.ChatType.PRIVATE:
            try:
                log_text = m.lang.get("log_new_user", "log_new_user").format(
                    user_id=m.from_user.id,
                    user_mention=m.from_user.mention
                )
                await app.send_message(
                    config.LOG_GROUP_ID, 
                    log_text
                )
            except Exception:
                pass

    me = await app.get_me()
    
    if m.chat.type == enums.ChatType.PRIVATE:
        text = m.lang.get("start_pm", "start_pm")
        reply_markup = start_pm_markup(me.username, m.lang)
    else:
        text = m.lang.get("start_gc", "start_gc")
        reply_markup = start_gc_markup(m.lang)

    if config.START_IMG:
        await m.reply_photo(
            photo=config.START_IMG,
            caption=text,
            reply_markup=reply_markup
        )
    else:
        await m.reply_text(text, reply_markup=reply_markup)


@app.on_callback_query(filters.regex("^help$"))
@lang.language()
async def help_cb(_, query: types.CallbackQuery):
    await query.answer("Help menu coming soon!", show_alert=True)


@app.on_message(filters.new_chat_members)
@lang.language()
async def on_new_chat_members(_, m: types.Message):
    if not config.LOG_GROUP_ID:
        return
        
    me = await app.get_me()
    for user in m.new_chat_members:
        if user.id == me.id:
            adder = m.from_user
            user_id = adder.id if adder else 0
            user_mention = adder.mention if adder else "Unknown"
            
            try:
                log_text = m.lang.get("log_new_chat", "log_new_chat").format(
                    chat_id=m.chat.id,
                    chat_title=m.chat.title,
                    user_id=user_id,
                    user_mention=user_mention
                )
                await app.send_message(
                    config.LOG_GROUP_ID, 
                    log_text
                )
            except Exception:
                pass
