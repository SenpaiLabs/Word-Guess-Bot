from pyrogram import filters, types
from Senpai import app
from Senpai.core.lang import lang
from Senpai.core.mongo import db
from Senpai.helpers._game_engine import engine
from Senpai.helpers._admins import admin_filter

@app.on_message(filters.command("end") & filters.group & admin_filter)
@lang.language()
async def end_game_cmd(_, m: types.Message):
    game = await db.get_active_game(m.chat.id)
    if not game:
        await m.reply_text(m.lang.get("end_game_no_active", "end_game_no_active"))
        return

    await engine.end_game(game)
    await m.reply_text(m.lang.get("end_game_ended_by_admin", "end_game_ended_by_admin").format(word=game.word.upper()))
