
from pyrogram import types

from Senpai.core.mongo import db
from Senpai.helpers._game_engine import GameAlreadyRunning, NoWordsAvailable, engine
from Senpai.helpers._board import renderer
from Senpai.helpers._dataclass import Group, User


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

    text = renderer.render_board(game, m.lang)
    if game.lucky_round:
        text = m.lang.get("lucky_round_banner", "lucky_round_banner") + "\n\n" + text

    sent = await m.reply_text(text)
    game.message_id = sent.id
    await db.save_game(game)
