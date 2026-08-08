from pyrogram import filters, types
from loguru import logger

from Senpai import app
from Senpai.core.mongo import db
from Senpai.core.lang import lang
from Senpai.helpers._sudo import extract_user
from config import config

@app.on_message(filters.command(["addsudo"]) & filters.user(config.OWNER_ID))
@lang.language()
async def _add_sudo(_, m: types.Message):
    user = await extract_user(m)
    if not user:
        return await m.reply_text(m.lang.get("user_not_found", "User not found."))

    if user.id in app.sudoers:
        return await m.reply_text(m.lang.get("sudo_already", "{} is already a sudo user.").format(user.mention))

    app.sudoers.add(user.id)
    await db.add_sudo(user.id)
    await m.reply_text(m.lang.get("sudo_added", "Added {} to sudo users.").format(user.mention))


@app.on_message(filters.command(["delsudo", "rmsudo"]) & filters.user(config.OWNER_ID))
@lang.language()
async def _del_sudo(_, m: types.Message):
    user = await extract_user(m)
    if not user:
        return await m.reply_text(m.lang.get("user_not_found", "User not found."))

    if user.id not in app.sudoers or user.id == config.OWNER_ID:
        return await m.reply_text(m.lang.get("sudo_not", "{} is not a sudo user or is the owner.").format(user.mention))

    app.sudoers.discard(user.id)
    await db.del_sudo(user.id)
    await m.reply_text(m.lang.get("sudo_removed", "Removed {} from sudo users.").format(user.mention))


_owner_mention = None

@app.on_message(filters.command(["listsudo", "sudolist"]) & filters.user(config.OWNER_ID))
@lang.language()
async def _listsudo(_, m: types.Message):
    global _owner_mention
    sent = await m.reply_text(m.lang.get("sudo_fetching", "Fetching sudo users..."))

    if not _owner_mention:
        try:
            owner = await app.get_users(config.OWNER_ID)
            _owner_mention = owner.mention
        except Exception as e:
            logger.debug(f"Failed to fetch owner: {e}")
            _owner_mention = f"Owner ({config.OWNER_ID})"

    txt = m.lang.get("sudo_owner", "👑 **Owner**\n- {}").format(_owner_mention)
    sudoers = await db.get_sudoers()
    
    if sudoers:
        txt += "\n\n" + m.lang.get("sudo_users", "⚡ **Sudo Users**")

    for user_id in sudoers:
        if user_id == config.OWNER_ID:
            continue
        try:
            user = await app.get_users(user_id)
            txt += f"\n- {user.mention}"
        except Exception:
            txt += f"\n- Unknown ({user_id})"

    await sent.edit_text(txt)
