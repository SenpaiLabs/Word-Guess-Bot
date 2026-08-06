from __future__ import annotations

from pyrogram import filters, types

from Senpai.core.mongo import db
from Senpai import app
from Senpai.helpers._dataclass import User
from Senpai.core.lang import get_string


@app.on_message(filters.command("start"))
async def start_cmd(_, m: types.Message):
    if m.from_user:
        await db.register_user(User(user_id=m.from_user.id, first_name=m.from_user.first_name, username=m.from_user.username))
    await m.reply_text(get_string("START_WELCOME"))
