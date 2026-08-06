"""
Local Wordle-style guess evaluator.

No AI involved — this is deterministic letter-matching logic.

🟩 Correct letter & correct position
🟨 Letter exists but wrong position
🟥 Letter doesn't exist (or all its occurrences are already accounted for)
"""

from __future__ import annotations

GREEN = "🟩"
YELLOW = "🟨"
RED = "🟥"


def evaluate_guess(guess: str, answer: str) -> str:
    """
    Standard two-pass Wordle algorithm that correctly handles
    duplicate letters (e.g. guessing "ELITE" against answer "LEVEL").
    """
    guess = guess.lower()
    answer = answer.lower()

    if len(guess) != len(answer):
        raise ValueError("Guess and answer must be the same length")

    length = len(answer)
    result = [RED] * length
    answer_letters = list(answer)

    # Pass 1 — greens (exact position matches consume the letter)
    for i in range(length):
        if guess[i] == answer_letters[i]:
            result[i] = GREEN
            answer_letters[i] = None  # consumed

    # Pass 2 — yellows (letter exists elsewhere, not yet consumed)
    for i in range(length):
        if result[i] == GREEN:
            continue
        if guess[i] in answer_letters:
            result[i] = YELLOW
            answer_letters[answer_letters.index(guess[i])] = None  # consume one occurrence

    return "".join(result)


def is_winning_pattern(pattern: str, length: int) -> bool:
    return pattern == GREEN * length
