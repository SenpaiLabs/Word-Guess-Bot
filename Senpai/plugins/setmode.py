from pyrogram import filters, types

from Senpai import app
from Senpai.core.mongo import db
from Senpai.core.lang import lang
from Senpai.helpers._admins import admin_filter

VALID_DIFFICULTIES = ("normal", "medium", "hard")


@app.on_message(filters.command("setmode") & filters.group & admin_filter)
@lang.language()
async def set_mode(_, m: types.Message):
    if len(m.command) < 2 or m.command[1].lower() not in VALID_DIFFICULTIES:
        await m.reply_text(m.lang.get("setmode_usage", "setmode_usage"))
        return

    difficulty = m.command[1].lower()
    await db.set_group_difficulty(m.chat.id, difficulty, title=m.chat.title or "")
    await m.reply_text(m.lang.get("setmode_success", "setmode_success").format(difficulty=difficulty.title()))
