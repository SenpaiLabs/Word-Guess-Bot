from __future__ import annotations

import os
import platform
import sys

import psutil
from pyrogram import filters, types
import pyrogram

from Senpai import app
from Senpai.core.lang import get_string
from Senpai.core.mongo import db
from Senpai.helpers._inline import get_support_markup
from config import config

@app.on_message(filters.command("stats"))
async def stats_cmd(_, m: types.Message):
    if config.START_IMG:
        reply = await m.reply_photo(
            photo=config.START_IMG,
            caption="Fetching stats..."
        )
    else:
        reply = await m.reply_text("Fetching stats...")
        
    sudos = 1 if config.OWNER_ID else 0
    chats = await db.groups.count_documents({})
    users = await db.users.count_documents({})
    
    modules = 0
    try:
        modules = len([f for f in os.listdir("Senpai/plugins") if f.endswith(".py") and not f.startswith("__")])
    except Exception:
        pass
    
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
    
    text = get_string("stats_text").format(
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
    
    reply_markup = get_support_markup()
    
    if config.START_IMG:
        await reply.edit_caption(caption=text, reply_markup=reply_markup)
    else:
        await reply.edit_text(text=text, reply_markup=reply_markup)
