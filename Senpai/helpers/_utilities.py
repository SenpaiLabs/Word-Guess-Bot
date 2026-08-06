from __future__ import annotations


def build_mention(user_id: int, name: str) -> str:
    safe_name = name or f"User {user_id}"
    return f'<a href="tg://user?id={user_id}">{safe_name}</a>'


def format_elapsed(seconds: int) -> str:
    if seconds < 60:
        return f"{seconds}s"
    minutes, sec = divmod(seconds, 60)
    if minutes < 60:
        return f"{minutes}m {sec}s"
    hours, minutes = divmod(minutes, 60)
    return f"{hours}h {minutes}m {sec}s"
