from __future__ import annotations

import asyncio
import importlib
import logging

from Senpai import app, scheduler, logger
from Senpai.core.mongo import db

_PLUGINS = [
    "Senpai.plugins.start",
    "Senpai.plugins.game",
    "Senpai.plugins.guess",
    "Senpai.plugins.leaderboard",
    "Senpai.plugins.mystats",
    "Senpai.plugins.ping",
    "Senpai.plugins.stats",
]


async def main() -> None:
    await db.connect()
    
    for plugin in _PLUGINS:
        try:
            importlib.import_module(plugin)
        except Exception:
            logger.exception(f"Failed to load plugin {plugin}")

    await app.start()

    scheduler.start()

    me = await app.get_me()
    logger.info(f"Senpai started as @{me.username}")

    stop_event = asyncio.Event()
    loop = asyncio.get_running_loop()
    import signal
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, stop_event.set)

    await stop_event.wait()

    logging.getLogger("asyncio").setLevel(logging.CRITICAL)

    scheduler.shutdown(wait=False)
    try:
        await app.stop()
    except Exception:
        pass
    await db.close()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        pass
