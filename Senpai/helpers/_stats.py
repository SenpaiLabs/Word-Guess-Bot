"""
Word Guess Bot - Statistics service

Wires a finished Game into per-user Statistics documents. Two documents
are kept per user: one scoped to the group (chat_id=<group>) and one
GLOBAL aggregate (chat_id=0), so /leaderboard and /gleaderboard can each
query a single collection without cross-group aggregation at read time.
"""

from __future__ import annotations

from Senpai.core.mongo import db
from Senpai.helpers._dataclass import Game, Statistics
from Senpai.helpers._badges import compute_badges
from Senpai.helpers._scoring import ScoreBreakdown, calculate_score

GLOBAL_SCOPE = 0


async def _bump_win(stats: Statistics, game: Game, breakdown: ScoreBreakdown) -> Statistics:
    stats.games_played += 1
    stats.games_won += 1
    stats.current_streak += 1
    stats.highest_streak = max(stats.highest_streak, stats.current_streak)
    stats.total_points += breakdown.total
    stats.total_guesses += game.attempts
    if breakdown.perfect:
        stats.perfect_guesses += 1
    if game.difficulty == "hard":
        stats.hard_wins += 1
    if stats.fastest_solve is None or game.elapsed_seconds < stats.fastest_solve:
        stats.fastest_solve = game.elapsed_seconds
    stats.badges = compute_badges(stats)
    return stats


async def _bump_loss(stats: Statistics, attempts_by_this_user: int) -> Statistics:
    stats.games_played += 1
    stats.games_lost += 1
    stats.current_streak = 0
    stats.total_guesses += attempts_by_this_user
    stats.badges = compute_badges(stats)
    return stats


async def apply_win(game: Game, winner_id: int) -> ScoreBreakdown:
    """Called once the winning guess is confirmed. Persists both scopes."""
    group_stats = await db.get_statistics(winner_id, game.chat_id)
    daily_first_win = await db.claim_daily_first_win(winner_id)

    breakdown = calculate_score(
        attempts=game.attempts,
        difficulty=game.difficulty,
        length=game.length,
        streak_after_this_win=group_stats.current_streak + 1,
        elapsed_seconds=game.elapsed_seconds,
        daily_first_win=daily_first_win,
        lucky_round=game.lucky_round,
    )

    group_stats = await _bump_win(group_stats, game, breakdown)
    await db.save_statistics(group_stats)

    global_stats = await db.get_statistics(winner_id, GLOBAL_SCOPE)
    global_stats = await _bump_win(global_stats, game, breakdown)
    await db.save_statistics(global_stats)

    return breakdown


async def apply_loss(game: Game) -> None:
    """
    Nobody guessed the word — every participant (anyone who submitted at
    least one guess) takes a loss and their streak resets.
    """
    attempts_by_user: dict[int, int] = {}
    for g in game.guesses:
        attempts_by_user[g.user_id] = attempts_by_user.get(g.user_id, 0) + 1

    for user_id, count in attempts_by_user.items():
        group_stats = await db.get_statistics(user_id, game.chat_id)
        group_stats = await _bump_loss(group_stats, count)
        await db.save_statistics(group_stats)

        global_stats = await db.get_statistics(user_id, GLOBAL_SCOPE)
        global_stats = await _bump_loss(global_stats, count)
        await db.save_statistics(global_stats)
