
from pyrogram import filters, types
from pyrogram.enums import ChatType, ParseMode

from Senpai.core.mongo import db
from Senpai import app
from Senpai.helpers._badges import TOP_PLAYER_BADGE
from Senpai.helpers._stats import GLOBAL_SCOPE
from Senpai.helpers._dataclass import Statistics, User
from Senpai.helpers._utilities import build_mention
from Senpai.core.lang import lang

RANK_EMOJI = {1: "🥇", 2: "🥈", 3: "🥉"}


def _rank_prefix(pos: int) -> str:
    return RANK_EMOJI.get(pos, f"{pos}.")


async def _render_leaderboard(chat_id: int, title: str, lang_dict: dict) -> str:
    top = await db.top_statistics(chat_id, limit=10)
    if not top:
        return lang_dict.get("leaderboard_no_games", "leaderboard_no_games").format(title=title)

    users = await db.get_users_map([s.user_id for s in top])

    lines = [title, ""]
    for pos, stats in enumerate(top, start=1):
        user = users.get(stats.user_id)
        name = user.first_name if user else str(stats.user_id)
        mention = build_mention(stats.user_id, name)
        badges = list(stats.badges)
        if pos == 1:
            badges.insert(0, TOP_PLAYER_BADGE)
        badge_text = f" {' '.join(b.split()[0] for b in badges)}" if badges else ""
        lines.append(
            f"{_rank_prefix(pos)} {mention}{badge_text} — <b>{stats.total_points}</b> pts "
            f"({stats.games_won}W/{stats.games_lost}L)"
        )

    return "\n".join(lines)


@app.on_message(filters.command("leaderboard") & filters.group)
@lang.language()
async def group_leaderboard(_, m: types.Message):
    title = m.lang.get("leaderboard_group_title", "leaderboard_group_title").format(chat_title=m.chat.title)
    text = await _render_leaderboard(m.chat.id, title, m.lang)
    await m.reply_text(text, parse_mode=ParseMode.HTML, disable_web_page_preview=True)


@app.on_message(filters.command("gleaderboard"))
@lang.language()
async def global_leaderboard(_, m: types.Message):
    title = m.lang.get("leaderboard_global_title", "leaderboard_global_title")
    text = await _render_leaderboard(GLOBAL_SCOPE, title, m.lang)
    await m.reply_text(text, parse_mode=ParseMode.HTML, disable_web_page_preview=True)


def _format_block(stats: Statistics, heading: str, lang_dict: dict) -> str:
    fastest = f"{stats.fastest_solve}s" if stats.fastest_solve is not None else lang_dict.get("userprofile_fastest_none", "None")
    badges = " ".join(stats.badges) if stats.badges else lang_dict.get("userprofile_badges_none", "None")
    return lang_dict.get("userprofile_block", "").format(
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


@app.on_message(filters.command("profile"))
@lang.language()
async def my_stats(_, m: types.Message):
    if m.from_user:
        await db.register_user(
            User(user_id=m.from_user.id, first_name=m.from_user.first_name, username=m.from_user.username)
        )

    user_id = m.from_user.id if m.from_user else 0
    sections = []

    if m.chat.type in (ChatType.GROUP, ChatType.SUPERGROUP):
        group_stats = await db.get_statistics(user_id, m.chat.id)
        heading = m.lang.get("userprofile_group_heading", "userprofile_group_heading").format(chat_title=m.chat.title)
        sections.append(_format_block(group_stats, heading, m.lang))

    global_stats = await db.get_statistics(user_id, GLOBAL_SCOPE)
    sections.append(_format_block(global_stats, m.lang.get("userprofile_global_heading", "userprofile_global_heading"), m.lang))

    await m.reply_text("\n\n".join(sections), parse_mode=ParseMode.HTML)
