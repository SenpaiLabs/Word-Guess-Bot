from pyrogram import filters, types
from pyrogram.enums import ParseMode

from Senpai import app
from Senpai.core.mongo import db
from Senpai.core.lang import lang
from Senpai.helpers._utilities import build_mention, format_elapsed


@app.on_message(filters.command("game") & filters.group)
@lang.language()
async def game_info(_, m: types.Message):
    game = await db.get_active_game(m.chat.id)
    if not game:
        await m.reply_text(m.lang.get("game_info_no_active", "game_info_no_active"))
        return

    starter_map = await db.get_users_map([game.started_by])
    starter = starter_map.get(game.started_by)
    starter_name = build_mention(game.started_by, starter.first_name if starter else str(game.started_by))
    text = m.lang.get("game_info_text", "game_info_text").format(
        length=game.length,
        attempts=game.attempts,
        starter=starter_name,
        elapsed=format_elapsed(game.elapsed_seconds),
        difficulty=game.difficulty.title(),
    )
    await m.reply_text(text, parse_mode=ParseMode.HTML)
