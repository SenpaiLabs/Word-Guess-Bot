from __future__ import annotations

from pyrogram import Client

from config import config

app = Client(
    name="word_guess_bot",
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    bot_token=config.BOT_TOKEN,
    plugins=dict(root="Senpai.plugins"),
)
