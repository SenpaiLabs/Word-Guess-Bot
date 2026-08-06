from __future__ import annotations

from pyrogram import Client

from config import config

app = Client(
    name="senpai",
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    bot_token=config.BOT_TOKEN,
)
