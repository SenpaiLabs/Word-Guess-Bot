
from __future__ import annotations

from config import config
from Senpai.helpers._dataclass import Game
from Senpai.core.lang import get_string

MODE_EMOJI = {4: "🍷", 5: "🍇", 6: "🍉"}


def render_board(game: Game) -> str:
    emoji = MODE_EMOJI.get(game.length, "🎯")
    header = get_string("board_header").format(
        emoji=emoji,
        length=game.length,
        attempts=game.attempts,
        max_attempts=config.MAX_ATTEMPTS,
    )

    lines = [header, ""]
    for g in game.guesses:
        lines.append(get_string("board_guess_line").format(guess=g.guess.upper(), pattern=g.pattern))

    return "\n".join(lines)


def render_result(game: Game, won: bool) -> str:
    if won:
        return get_string("result_win").format(attempts=game.attempts, word=game.word.upper())
    return get_string("result_lose").format(word=game.word.upper())
