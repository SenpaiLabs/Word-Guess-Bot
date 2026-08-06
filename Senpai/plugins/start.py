from __future__ import annotations

from pyrogram import filters, types

from Senpai.core.mongo import db
from Senpai import app
from Senpai.helpers._dataclass import User

WELCOME = (
    "👋 **Word Guess Bot**\n\n"
    "Guess the hidden word letter by letter — Wordle style, right inside "
    "your Telegram groups.\n\n"
    "Add me to a group and try:\n"
    "/new — random length game\n"
    "/new4, /new5, /new6 — pick a specific length\n"
    "/game — see the current game's info\n"
    "/leaderboard — top players in this group\n"
    "/mystats — your personal stats"
)


@app.on_message(filters.command("start"))
async def start_cmd(_, m: types.Message):
    if m.from_user:
        await db.register_user(User(user_id=m.from_user.id, first_name=m.from_user.first_name, username=m.from_user.username))
    await m.reply_text(WELCOME)
