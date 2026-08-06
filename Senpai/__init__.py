from __future__ import annotations

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from config import config, logger

config.validate()

from Senpai.core.bot import app

scheduler = AsyncIOScheduler()

__all__ = ["app", "scheduler", "config", "logger"]
