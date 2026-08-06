"""
Word Guess Bot - Game Engine

Pure game logic, decoupled from Telegram. Handlers (Phase 4) call into
this layer; this layer never touches Pyrogram directly.
"""

from __future__ import annotations

import asyncio
import random
from time import time

from config import config
from Senpai.core.mongo import db
from Senpai.helpers._evaluator import evaluate_guess, is_winning_pattern
from Senpai.helpers._dataclass import Game, GuessResult
from Senpai.helpers._word_generator import maybe_replenish


class GameAlreadyRunning(Exception):
    """Raised when /new is used while a game is already active in the chat."""


class NoWordsAvailable(Exception):
    """Raised when the word pool for a mode/difficulty is completely empty."""


class GameEngine:
    VALID_LENGTHS = (4, 5, 6)

    async def start_game(
        self, chat_id: int, started_by: int, length: int | None = None
    ) -> Game:
        """
        Start a new game. `length=None` triggers random mode
        (equal probability across 4/5/6 letters).
        """
        if await db.get_active_game(chat_id):
            raise GameAlreadyRunning

        if length is None:
            length = random.choice(self.VALID_LENGTHS)
        elif length not in self.VALID_LENGTHS:
            raise ValueError(f"Unsupported word length: {length}")

        difficulty = await db.get_group_difficulty(chat_id)
        word = await db.get_random_word(chat_id, length, difficulty)
        if not word:
            raise NoWordsAvailable(f"No {length}-letter words available for difficulty={difficulty}")

        lucky_round = random.random() < config.LUCKY_ROUND_CHANCE

        game = Game(
            chat_id=chat_id,
            word=word.word,
            length=length,
            difficulty=difficulty,
            started_by=started_by,
            lucky_round=lucky_round,
        )
        await db.save_game(game)

        # Fire-and-forget: top up the word pool in the background if it's
        # running low. Never blocks this call, never runs on every game.
        asyncio.create_task(maybe_replenish(chat_id, length, difficulty))

        return game

    async def process_guess(self, game: Game, guess: str, user_id: int) -> tuple[str, bool, bool]:
        """
        Evaluate a guess against the active game.

        Returns (pattern, won, game_over).
        game_over is True if won OR max attempts reached.
        """
        guess = guess.strip().lower()
        pattern = evaluate_guess(guess, game.word)
        won = is_winning_pattern(pattern, game.length)

        game.guesses.append(GuessResult(guess=guess, pattern=pattern, user_id=user_id))

        game_over = won or game.attempts >= config.MAX_ATTEMPTS

        if won:
            game.status = "won"
            game.winner_id = user_id
        elif game_over:
            game.status = "lost"

        if game_over:
            game.ended_at = time()
            await db.finish_game(game)
        else:
            await db.save_game(game)

        return pattern, won, game_over

    async def end_game(self, game: Game) -> None:
        """Admin-triggered /end — reveal answer and close the game state."""
        game.status = "ended"
        game.ended_at = time()
        await db.finish_game(game)

    def is_guess_shape_valid(self, guess: str, length: int) -> bool:
        return len(guess) == length and guess.isalpha()


engine = GameEngine()
