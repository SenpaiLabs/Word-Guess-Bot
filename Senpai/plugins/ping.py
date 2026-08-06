from __future__ import annotations

import time
import psutil
from pyrogram import filters, types
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from Senpai import app
from Senpai.core.lang import get_string
from config import config

# Store bot start time to calculate uptime
BOT_START_TIME = time.time()

def get_readable_time(seconds: int) -> str:
    count = 0
    ping_time = ""
    time_list = []
    time_suffix_list = ["s", "m", "h", "days"]
    while count < 4:
        count += 1
        remainder, result = divmod(seconds, 60) if count < 3 else divmod(seconds, 24)
        if seconds == 0 and remainder == 0:
            break
        time_list.append(int(result))
        seconds = int(remainder)
    
    for x in range(len(time_list)):
        time_list[x] = str(time_list[x]) + time_suffix_list[x]
    
    if len(time_list) == 4:
        ping_time += f"{time_list[3]}, {time_list[2]}:{time_list[1]}:{time_list[0]}"
    elif len(time_list) == 3:
        ping_time += f"{time_list[2]}:{time_list[1]}:{time_list[0]}"
    elif len(time_list) == 2:
        ping_time += f"{time_list[1]}:{time_list[0]}"
    elif len(time_list) == 1:
        ping_time += time_list[0]
    return ping_time if ping_time else "0s"

@app.on_message(filters.command("ping"))
async def ping_cmd(_, m: types.Message):
    start_t = time.time()
    
    if config.START_IMG:
        reply = await m.reply_photo(
            photo=config.START_IMG,
            caption="Pinging..."
        )
    else:
        reply = await m.reply_text("Pinging...")
        
    end_t = time.time()
    
    latency = round((end_t - start_t) * 1000, 2)
    uptime = get_readable_time(int(time.time() - BOT_START_TIME))
    
    cpu = psutil.cpu_percent(interval=0.5)
    ram = psutil.virtual_memory().percent
    disk = psutil.disk_usage("/").percent
    
    text = get_string("PING_TEXT").format(
        latency=latency,
        uptime=uptime,
        cpu=cpu,
        ram=ram,
        disk=disk
    )
    
    reply_markup = None
    if config.SUPPORT_CHAT:
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton(get_string("SUPPORT_BUTTON"), url=config.SUPPORT_CHAT)]
        ])
    
    if config.START_IMG:
        await reply.edit_caption(caption=text, reply_markup=reply_markup)
    else:
        await reply.edit_text(text=text, reply_markup=reply_markup)
