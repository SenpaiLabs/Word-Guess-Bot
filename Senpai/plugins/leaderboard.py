from __future__ import annotations

from pyrogram import filters, types
from pyrogram.enums import ParseMode

from Senpai.core.mongo import db
from Senpai import app
from Senpai.helpers._badges import TOP_PLAYER_BADGE
from Senpai.helpers._stats import GLOBAL_SCOPE
from Senpai.helpers._utilities import build_mention
from Senpai.core.lang import lang

RANK_EMOJI = {1: "🥇", 2: "🥈", 3: "🥉"}


def _rank_prefix(pos: int) -> str:
    return RANK_EMOJI.get(pos, f"{pos}.")


async def _render_leaderboard(chat_id: int, title: str) -> str:
    top = await db.top_statistics(chat_id, limit=10)
    if not top:
        return m.lang.get("leaderboard_no_games", "leaderboard_no_games").format(title=title)

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
    text = await _render_leaderboard(m.chat.id, title)
    await m.reply_text(text, parse_mode=ParseMode.HTML, disable_web_page_preview=True)


@app.on_message(filters.command("gleaderboard"))
@lang.language()
async def global_leaderboard(_, m: types.Message):
    title = m.lang.get("leaderboard_global_title", "leaderboard_global_title")
    text = await _render_leaderboard(GLOBAL_SCOPE, title)
    await m.reply_text(text, parse_mode=ParseMode.HTML, disable_web_page_preview=True)
