
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import config

config.check()

from Senpai.core.bot import app

scheduler = AsyncIOScheduler()

__all__ = ["app", "scheduler", "config"]
