from __future__ import annotations

from pyrogram import filters, types
from pyrogram.enums import ChatType, ParseMode

from Senpai.core.mongo import db
from Senpai import app
from Senpai.helpers._dataclass import Statistics, User
from Senpai.helpers._stats import GLOBAL_SCOPE


def _format_block(stats: Statistics, heading: str) -> str:
    fastest = f"{stats.fastest_solve}s" if stats.fastest_solve is not None else "—"
    badges = " ".join(stats.badges) if stats.badges else "None yet"
    return (
        f"<b>{heading}</b>\n"
        f"Games Played: {stats.games_played}\n"
        f"Games Won: {stats.games_won}\n"
        f"Games Lost: {stats.games_lost}\n"
        f"Total Points: {stats.total_points}\n"
        f"Current Streak: {stats.current_streak}\n"
        f"Highest Streak: {stats.highest_streak}\n"
        f"Fastest Solve: {fastest}\n"
        f"Perfect Guesses: {stats.perfect_guesses}\n"
        f"Total Guesses: {stats.total_guesses}\n"
        f"Average Attempts: {stats.average_attempts}\n"
        f"Badges: {badges}"
    )


@app.on_message(filters.command("mystats"))
async def my_stats(_, m: types.Message):
    if m.from_user:
        await db.register_user(
            User(user_id=m.from_user.id, first_name=m.from_user.first_name, username=m.from_user.username)
        )

    user_id = m.from_user.id if m.from_user else 0
    sections = []

    if m.chat.type in (ChatType.GROUP, ChatType.SUPERGROUP):
        group_stats = await db.get_statistics(user_id, m.chat.id)
        sections.append(_format_block(group_stats, f"📊 Stats in {m.chat.title}"))

    global_stats = await db.get_statistics(user_id, GLOBAL_SCOPE)
    sections.append(_format_block(global_stats, "🌍 Global Stats"))

    await m.reply_text("\n\n".join(sections), parse_mode=ParseMode.HTML)
