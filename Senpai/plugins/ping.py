from __future__ import annotations

import time
import psutil
from pyrogram import filters, types

from Senpai import app
from Senpai.helpers._inline import get_support_markup
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
    
    if config.PING_IMG:
        reply = await m.reply_photo(
            photo=config.PING_IMG,
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
    
    text = get_string("ping_text").format(
        latency=latency,
        uptime=uptime,
        cpu=cpu,
        ram=ram,
        disk=disk
    )
    
    reply_markup = get_support_markup()
    
    if config.PING_IMG:
        await reply.edit_caption(caption=text, reply_markup=reply_markup)
    else:
        await reply.edit_text(text=text, reply_markup=reply_markup)
