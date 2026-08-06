"""
Word Guess Bot - Badges

Persistent, per-user badges (recomputed after every stat update).
"Top Player" (👑) is NOT stored here — it's rank-dependent and awarded
dynamically at leaderboard render time, since it shifts as others play.
"""

from __future__ import annotations

from Senpai.helpers._dataclass import Statistics

WIN_STREAK_THRESHOLD = 5
SPEED_MASTER_SECONDS = 60
HARD_MODE_MASTER_WINS = 10
PERFECT_GUESSER_COUNT = 5

TOP_PLAYER_BADGE = "👑 Top Player"

BADGE_RULES: dict[str, callable] = {
    "🔥 Win Streak": lambda s: s.current_streak >= WIN_STREAK_THRESHOLD,
    "⚡ Speed Master": lambda s: s.fastest_solve is not None and s.fastest_solve <= SPEED_MASTER_SECONDS,
    "💎 Hard Mode Master": lambda s: s.hard_wins >= HARD_MODE_MASTER_WINS,
    "🎯 Perfect Guesser": lambda s: s.perfect_guesses >= PERFECT_GUESSER_COUNT,
}


def compute_badges(stats: Statistics) -> list[str]:
    return [name for name, rule in BADGE_RULES.items() if rule(stats)]
