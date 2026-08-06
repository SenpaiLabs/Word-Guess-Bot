"""
Renders the single, edited game message.
"""

from __future__ import annotations

from config import config
from Senpai.helpers._dataclass import Game

MODE_EMOJI = {4: "🍷", 5: "🍇", 6: "🍉"}


def render_board(game: Game) -> str:
    emoji = MODE_EMOJI.get(game.length, "🎯")
    header = f"{emoji} ⌞ {game.length}-L Mode ⌝ 〢{game.attempts}/{config.MAX_ATTEMPTS}"

    lines = [header, ""]
    for g in game.guesses:
        lines.append(f"{g.guess.upper()} → {g.pattern}")

    return "\n".join(lines)


def render_result(game: Game, won: bool) -> str:
    if won:
        return f"🎉 Solved in {game.attempts} attempts!\n\nAnswer: {game.word.upper()}"
    return f"❌ Nobody guessed the word.\n\nAnswer:\n{game.word.upper()}"
