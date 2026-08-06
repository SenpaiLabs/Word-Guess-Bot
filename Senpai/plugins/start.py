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
                await app.send_message(
                    config.LOG_GROUP_ID, 
                    f"👤 **New User Started Bot:**\n{m.from_user.mention} (`{m.from_user.id}`)"
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
            adder = m.from_user.mention if m.from_user else "Unknown"
            try:
                await app.send_message(
                    config.LOG_GROUP_ID, 
                    f"🎉 **Bot Added to Group!**\n**Group:** {m.chat.title} (`{m.chat.id}`)\n**Added By:** {adder}"
                )
            except Exception:
                pass
