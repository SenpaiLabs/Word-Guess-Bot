from __future__ import annotations

from pyrogram import filters, types
from pyrogram.errors import MessageIdInvalid, MessageNotModified

from Senpai.core.mongo import db
from Senpai.helpers._game_engine import engine
from Senpai.helpers._board import render_board, render_result
from Senpai import app
from Senpai.helpers._dataclass import User
from Senpai.helpers import _stats as stats_service
from Senpai.core.lang import get_string


def _looks_like_guess(_, __, m: types.Message) -> bool:
    if not m.text or m.text.startswith("/"):
        return False
    return m.text.strip().isalpha()


guess_filter = filters.create(_looks_like_guess)


@app.on_message(filters.group & guess_filter, group=1)
async def handle_guess(_, m: types.Message):
    game = await db.get_active_game(m.chat.id)
    if not game:
        return

    guess = m.text.strip().lower()
    if not engine.is_guess_shape_valid(guess, game.length):
        return  # silently ignore — not a guess for this game's word length

    if m.from_user:
        await db.register_user(
            User(user_id=m.from_user.id, first_name=m.from_user.first_name, username=m.from_user.username)
        )

    pattern, won, game_over = await engine.process_guess(game, guess, m.from_user.id if m.from_user else 0)

    # Keep the chat clean — remove the raw guess message if we're allowed to.
    try:
        await m.delete()
    except Exception:
        pass

    board_text = render_board(game)
    if game_over:
        board_text += "\n\n" + render_result(game, won)
        if won:
            breakdown = await stats_service.apply_win(game, m.from_user.id)
            board_text += "\n\n" + "\n".join(breakdown.as_lines())
            board_text += get_string("POINTS_TOTAL").format(total=breakdown.total)
        else:
            await stats_service.apply_loss(game)

    if not game.message_id:
        sent = await app.send_message(chat_id=m.chat.id, text=board_text)
        game.message_id = sent.id
        await db.save_game(game) if not game_over else await db.finish_game(game)
        return

    try:
        await app.edit_message_text(chat_id=m.chat.id, message_id=game.message_id, text=board_text)
    except (MessageIdInvalid, MessageNotModified):
        pass
    except Exception:
        # message may have been deleted — resend as a fresh board
        sent = await app.send_message(chat_id=m.chat.id, text=board_text)
        game.message_id = sent.id
        await db.save_game(game) if not game_over else await db.finish_game(game)
