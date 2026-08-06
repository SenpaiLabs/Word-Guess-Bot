from __future__ import annotations

from pyrogram import filters, types, enums

from Senpai.core.mongo import db
from Senpai import app
from Senpai.helpers._dataclass import User
from Senpai.core.lang import get_string
from config import config


@app.on_message(filters.command("start"))
async def start_cmd(_, m: types.Message):
    if m.from_user:
        await db.register_user(User(user_id=m.from_user.id, first_name=m.from_user.first_name, username=m.from_user.username))
        
        if config.LOG_GROUP_ID and m.chat.type == enums.ChatType.PRIVATE:
            try:
                log_text = get_string("LOG_NEW_USER").format(
                    user_id=m.from_user.id,
                    user_mention=m.from_user.mention
                )
                await app.send_message(
                    config.LOG_GROUP_ID, 
                    log_text
                )
            except Exception:
                pass

    if config.START_IMG:
        await m.reply_photo(
            photo=config.START_IMG,
            caption=get_string("START_WELCOME")
        )
    else:
        await m.reply_text(get_string("START_WELCOME"))


@app.on_message(filters.new_chat_members)
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
                log_text = get_string("LOG_NEW_CHAT").format(
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
