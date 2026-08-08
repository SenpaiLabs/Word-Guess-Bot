import os
import asyncio
from loguru import logger

from pyrogram import errors, filters, types

from Senpai import app
from Senpai.core.lang import lang
from Senpai.core.mongo import db
from Senpai.helpers._sudo import sudo_filter

broadcasting = asyncio.Lock()

@app.on_message(filters.command(["broadcast"]) & sudo_filter)
@lang.language()
async def _broadcast(_, message: types.Message):
    if not message.reply_to_message:
        return await message.reply_text(message.lang.get("gcast_usage", "Please reply to a message to broadcast it."))

    if broadcasting.locked():
        return await message.reply_text(message.lang.get("gcast_active", "A broadcast is already in progress. Please wait."))

    msg = message.reply_to_message
    copy = "-copy" in message.command
    count, ucount = 0, 0
    groups, users = set(), set()
    sent = await message.reply_text(message.lang.get("gcast_start", "Broadcast started..."))

    if "-nochat" not in message.command:
        groups = set(await db.get_chats())
    if "-user" in message.command:
        users = set(await db.get_users())

    chats = list(groups | users)
    failed = None

    async with broadcasting:
        for chat in chats:
            try:
                if copy:
                    await msg.copy(chat, reply_markup=msg.reply_markup)
                else:
                    await msg.forward(chat)
                    
                if chat in groups:
                    count += 1
                else:
                    ucount += 1
                await asyncio.sleep(0.2)
            except errors.FloodWait as fw:
                await asyncio.sleep(fw.value + 10)
            except Exception as ex:
                if not failed:
                    failed = open("errors.txt", "w")
                failed.write(f"{chat} - {ex}\n")
                continue

    text = message.lang.get("gcast_end", "Broadcast finished!\n\nGroups: {}\nUsers: {}").format(count, ucount)
    if failed:
        failed.close()
        await message.reply_document(
            document="errors.txt",
            caption=text,
        )
        try: 
            os.remove("errors.txt")
        except Exception as e: 
            logger.debug(f"Failed to remove errors.txt: {e}")

    await sent.edit_text(text)
