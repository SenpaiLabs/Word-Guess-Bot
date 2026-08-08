
import os
import platform
import sys

import psutil
from pyrogram import filters, types
import pyrogram
from loguru import logger

from Senpai import app
from Senpai.core.lang import lang
from Senpai.core.mongo import db
from Senpai.helpers._inline import inline
from config import config

@app.on_message(filters.command("stats"))
@lang.language()
async def stats_cmd(_, m: types.Message):
    if config.PING_IMG:
        reply = await m.reply_photo(
            photo=config.PING_IMG,
            caption=m.lang.get("stats_fetch", "Fetching stats...")
        )
    else:
        reply = await m.reply_text(m.lang.get("stats_fetch", "Fetching stats..."))
        
    sudos = len(app.sudoers)
    chats = await db.groupsdb.count_documents({})
    users = await db.usersdb.count_documents({})
    
    modules = 0
    try:
        modules = len([f for f in os.listdir("Senpai/plugins") if f.endswith(".py") and not f.startswith("__")])
    except Exception as e:
        logger.debug(f"Failed to count modules: {e}")
    
    plat = platform.system()
    
    ram_used = round(psutil.virtual_memory().used / (1024 * 1024), 2)
    ram_total = round(psutil.virtual_memory().total / (1024 * 1024 * 1024), 2)
    
    cpu = psutil.cpu_percent(interval=0.5)
    cpu_cores = psutil.cpu_count()
    
    disk_used = round(psutil.disk_usage("/").used / (1024 * 1024 * 1024), 2)
    disk_total = round(psutil.disk_usage("/").total / (1024 * 1024 * 1024), 2)
    
    python_version = sys.version.split()[0]
    pyrogram_version = pyrogram.__version__
    
    me = await app.get_me()
    bot_name = me.first_name
    
    text = m.lang.get("stats_text", "stats_text").format(
        bot_name=bot_name,
        sudos=sudos,
        chats=chats,
        users=users,
        modules=modules,
        platform=plat,
        ram_used=ram_used,
        ram_total=ram_total,
        cpu=cpu,
        cpu_cores=cpu_cores,
        disk_used=disk_used,
        disk_total=disk_total,
        python_version=python_version,
        pyrogram_version=pyrogram_version
    )
    
    reply_markup = inline.support_markup(m.lang)
    
    if config.PING_IMG:
        await reply.edit_caption(caption=text, reply_markup=reply_markup)
    else:
        await reply.edit_text(text=text, reply_markup=reply_markup)
