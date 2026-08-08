import os
import sys
import shutil

from pyrogram import filters, types
from loguru import logger
from config import config

from Senpai import app
from Senpai.core.lang import lang
from Senpai.helpers._sudo import sudo_filter


@app.on_message(filters.command("logs") & sudo_filter)
@lang.language()
async def _logs(_, m: types.Message):
    sent = await m.reply_text(m.lang.get("log_fetch", "Fetching logs..."))
    if not os.path.exists("log.txt"):
        return await sent.edit_text(m.lang.get("log_not_found", "Log file not found!"))
        
    await sent.delete()
    await m.reply_document(
        document="log.txt",
        caption=m.lang.get("log_sent", "Here are the logs").format(app.name),
    )


@app.on_message(filters.command("restart") & sudo_filter)
@lang.language()
async def _restart(_, m: types.Message):
    sent = await m.reply_text(m.lang.get("restarting", "Restarting..."))

    for directory in ["cache", "downloads", "words"]:
        shutil.rmtree(directory, ignore_errors=True)

    await sent.edit_text(m.lang.get("restarted", "Restarted Successfully! Wait for it to boot back up."))
    
    try: 
        os.remove("log.txt")
    except Exception as e: 
        logger.debug(f"Failed to remove log.txt: {e}")

    os.execl(sys.executable, sys.executable, "-m", "Senpai.main")
