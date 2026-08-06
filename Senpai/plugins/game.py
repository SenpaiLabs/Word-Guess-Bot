from __future__ import annotations

from pyrogram import filters, types
from pyrogram.enums import ParseMode

from Senpai.core.mongo import db
from Senpai.helpers._game_engine import GameAlreadyRunning, NoWordsAvailable, engine
from Senpai.helpers._board import render_board
from Senpai.helpers._admins import admin_filter
from Senpai import app
from Senpai.helpers._dataclass import Group, User
from Senpai.helpers._utilities import build_mention, format_elapsed
from Senpai.core.lang import lang

VALID_DIFFICULTIES = ("normal", "medium", "hard")


async def _register(m: types.Message) -> None:
    if m.from_user:
        await db.register_user(
            User(user_id=m.from_user.id, first_name=m.from_user.first_name, username=m.from_user.username)
        )
    await db.register_group(Group(chat_id=m.chat.id, title=m.chat.title or ""))


async def _start_game(m: types.Message, length: int | None) -> None:
    await _register(m)
    try:
        game = await engine.start_game(m.chat.id, m.from_user.id, length=length)
    except GameAlreadyRunning:
        await m.reply_text(m.lang.get("game_already_running", "game_already_running"))
        return
    except NoWordsAvailable:
        await m.reply_text(m.lang.get("no_words_available", "no_words_available"))
        return

    text = render_board(game, m.lang)
    if game.lucky_round:
        text = m.lang.get("lucky_round_banner", "lucky_round_banner") + "\n\n" + text

    sent = await m.reply_text(text)
    game.message_id = sent.id
    await db.save_game(game)


@app.on_message(filters.command("new") & filters.group)
@lang.language()
async def new_random(_, m: types.Message):
    await _start_game(m, length=None)


@app.on_message(filters.command("new4") & filters.group)
@lang.language()
async def new4(_, m: types.Message):
    await _start_game(m, length=4)


@app.on_message(filters.command("new5") & filters.group)
@lang.language()
async def new5(_, m: types.Message):
    await _start_game(m, length=5)


@app.on_message(filters.command("new6") & filters.group)
@lang.language()
async def new6(_, m: types.Message):
    await _start_game(m, length=6)


@app.on_message(filters.command("end") & filters.group & admin_filter)
@lang.language()
async def end_game_cmd(_, m: types.Message):
    game = await db.get_active_game(m.chat.id)
    if not game:
        await m.reply_text(m.lang.get("end_game_no_active", "end_game_no_active"))
        return

    await engine.end_game(game)
    await m.reply_text(m.lang.get("end_game_ended_by_admin", "end_game_ended_by_admin").format(word=game.word.upper()))


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


@app.on_message(filters.command("setmode") & filters.group & admin_filter)
@lang.language()
async def set_mode(_, m: types.Message):
    if len(m.command) < 2 or m.command[1].lower() not in VALID_DIFFICULTIES:
        await m.reply_text(m.lang.get("setmode_usage", "setmode_usage"))
        return

    difficulty = m.command[1].lower()
    await db.set_group_difficulty(m.chat.id, difficulty, title=m.chat.title or "")
    await m.reply_text(m.lang.get("setmode_success", "setmode_success").format(difficulty=difficulty.title()))
