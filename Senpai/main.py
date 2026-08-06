from __future__ import annotations

import asyncio
import signal

from Senpai import app, scheduler, logger
from Senpai.core.mongo import db


async def main() -> None:
    await db.connect()
    await app.start()
    scheduler.start()

    me = await app.get_me()
    logger.info(f"Word Guess Bot started as @{me.username}")

    stop_event = asyncio.Event()

    # Graceful shutdown on SIGINT (Ctrl+C) and SIGTERM
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, stop_event.set)

    await stop_event.wait()

    logger.info("Shutting down gracefully...")
    scheduler.shutdown(wait=False)
    await app.stop()
    await db.close()
    logger.info("Bye!")


if __name__ == "__main__":
    asyncio.run(main())
