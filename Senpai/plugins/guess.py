
import asyncio
from loguru import logger

from pyrogram import filters, types

from Senpai.core.mongo import db
from Senpai.helpers._game_engine import engine
from Senpai.helpers._board import renderer
from Senpai import app
from Senpai.helpers._dataclass import User
from Senpai.helpers import _stats as stats_service
from Senpai.core.lang import lang


async def delete_temp_message(message: types.Message, delay: int = 3):
    await asyncio.sleep(delay)
    try:
        await message.delete()
    except Exception as e:
        logger.debug(f"Failed to delete temp message: {e}")


def _looks_like_guess(_, __, m: types.Message) -> bool:
    if not m.text or m.text.startswith("/"):
        return False
    return m.text.strip().isalpha()


guess_filter = filters.create(_looks_like_guess)


@app.on_message(filters.group & guess_filter, group=1)
@lang.language()
async def handle_guess(_, m: types.Message):
    game = await db.get_active_game(m.chat.id)
    if not game:
        return

    guess = m.text.strip().lower()
    if not engine.is_guess_shape_valid(guess, game.length):
        return

    # Check if already guessed
    if any(g.guess == guess for g in game.guesses):
        msg_text = m.lang.get("guess_already_guessed", "guess_already_guessed").format(guess=guess.upper())
        temp = await m.reply_text(msg_text)
        asyncio.create_task(delete_temp_message(temp))
        return

    # Check if the word is valid (exists in dictionary)
    if not await db.is_valid_word(guess):
        msg_text = m.lang.get("guess_invalid_word", "guess_invalid_word").format(guess=guess.upper())
        temp = await m.reply_text(msg_text)
        asyncio.create_task(delete_temp_message(temp))
        return

    if m.from_user:
        await db.register_user(
            User(user_id=m.from_user.id, first_name=m.from_user.first_name, username=m.from_user.username)
        )

    pattern, won, game_over = await engine.process_guess(game, guess, m.from_user.id if m.from_user else 0)

    board_text = renderer.render_board(game, m.lang)
    result_text = None
    if game_over:
        result_text = renderer.render_result(game, won, m.lang)
        if won:
            breakdown = await stats_service.apply_win(game, m.from_user.id)
            result_text += "\n\n" + "\n".join(breakdown.as_lines())
            result_text += m.lang.get("points_total", "points_total").format(total=breakdown.total)
        else:
            await stats_service.apply_loss(game)

    # Send the new board message
    sent = await app.send_message(chat_id=m.chat.id, text=board_text)
    game.message_id = sent.id
    
    if game_over:
        await db.finish_game(game)
        if result_text:
            # Send the congratulation/result message separately, replying to the winning guess
            await app.send_message(chat_id=m.chat.id, text=result_text, reply_to_message_id=m.id)
    else:
        await db.save_game(game)
