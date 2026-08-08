from pyrogram import filters, types
from Senpai import app

async def _is_sudo(_, __, message: types.Message) -> bool:
    if not message.from_user:
        return False
    return message.from_user.id in app.sudoers

sudo_filter = filters.create(_is_sudo)

async def extract_user(message: types.Message) -> types.User | None:
    """Extract a user from a reply or command argument."""
    if message.reply_to_message and message.reply_to_message.from_user:
        return message.reply_to_message.from_user

    if len(message.command) > 1:
        query = message.command[1]
        try:
            return await app.get_users(query)
        except Exception:
            return None

    return None
