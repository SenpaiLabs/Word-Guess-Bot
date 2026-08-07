from pyrogram import filters, types
from Senpai import app
from Senpai.core.lang import lang
from Senpai.plugins.game import _start_game


@app.on_message(filters.command(["new", "new4", "new5", "new6"]) & filters.group)
@lang.language()
async def new_random(_, m: types.Message):
    cmd = m.command[0].lower()
    length = None
    if cmd == "new4":
        length = 4
    elif cmd == "new5":
        length = 5
    elif cmd == "new6":
        length = 6
        
    await _start_game(m, length=length)
