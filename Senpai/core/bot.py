
from pyrogram import Client

from config import config

class Bot(Client):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.sudoers: set = set()

app = Bot(
    name="senpai",
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    bot_token=config.BOT_TOKEN,
)
