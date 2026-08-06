from __future__ import annotations

import asyncio

from Senpai import app, scheduler, logger
from Senpai.core.mongo import db


async def main() -> None:
    await db.connect()
    await app.start()
    scheduler.start()

    me = await app.get_me()
    logger.info(f"Word Guess Bot started as @{me.username}")

    try:
        await asyncio.Event().wait()
    finally:
        scheduler.shutdown(wait=False)
        await app.stop()
        await db.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Shutting down...")
