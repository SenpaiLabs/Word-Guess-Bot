
import asyncio
import importlib
import signal

from loguru import logger

from Senpai import app, scheduler
from Senpai.core.mongo import db

from Senpai.plugins import all_modules


async def main() -> None:
    logger.add("log.txt", level="INFO")
    await db.connect()
    
    app.sudoers = set(await db.get_sudoers())
    from config import config
    if config.OWNER_ID:
        app.sudoers.add(config.OWNER_ID)
    
    for module in all_modules:
        try:
            importlib.import_module(f"Senpai.plugins.{module}")
        except Exception:
            logger.exception(f"Failed to load plugin {module}")
            
    logger.info(f"Loaded {len(all_modules)} modules.")

    await app.start()

    scheduler.start()

    me = await app.get_me()
    logger.info(f"Senpai started as @{me.username}")
    
    from config import config
    if config.LOGGER_ID:
        try:
            await app.send_message(config.LOGGER_ID, f"✅ Bot started as @{me.username}")
        except Exception as e:
            logger.debug(f"Failed to send startup message: {e}")

    stop_event = asyncio.Event()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, stop_event.set)

    await stop_event.wait()
    logger.info("Stopping...")

    scheduler.shutdown(wait=False)
    try:
        await app.stop()
    except Exception as e:
        logger.debug(f"Failed to stop app gracefully: {e}")
    await db.close()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        pass
