from __future__ import annotations

from pyrogram import filters, types
from pyrogram.enums import ChatType, ParseMode

from Senpai.core.mongo import db
from Senpai import app
from Senpai.helpers._dataclass import Statistics, User
from Senpai.helpers._stats import GLOBAL_SCOPE
from Senpai.core.lang import get_string


def _format_block(stats: Statistics, heading: str) -> str:
    fastest = f"{stats.fastest_solve}s" if stats.fastest_solve is not None else get_string("userprofile_fastest_none")
    badges = " ".join(stats.badges) if stats.badges else get_string("userprofile_badges_none")
    return get_string("userprofile_block").format(
        heading=heading,
        games_played=stats.games_played,
        games_won=stats.games_won,
        games_lost=stats.games_lost,
        total_points=stats.total_points,
        current_streak=stats.current_streak,
        highest_streak=stats.highest_streak,
        fastest_solve=fastest,
        perfect_guesses=stats.perfect_guesses,
        total_guesses=stats.total_guesses,
        average_attempts=stats.average_attempts,
        badges=badges,
    )


@app.on_message(filters.command("userprofile"))
async def my_stats(_, m: types.Message):
    if m.from_user:
        await db.register_user(
            User(user_id=m.from_user.id, first_name=m.from_user.first_name, username=m.from_user.username)
        )

    user_id = m.from_user.id if m.from_user else 0
    sections = []

    if m.chat.type in (ChatType.GROUP, ChatType.SUPERGROUP):
        group_stats = await db.get_statistics(user_id, m.chat.id)
        heading = get_string("userprofile_group_heading").format(chat_title=m.chat.title)
        sections.append(_format_block(group_stats, heading))

    global_stats = await db.get_statistics(user_id, GLOBAL_SCOPE)
    sections.append(_format_block(global_stats, get_string("userprofile_global_heading")))

    await m.reply_text("\n\n".join(sections), parse_mode=ParseMode.HTML)
