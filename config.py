

import logging
from dataclasses import dataclass, field

from dotenv import load_dotenv
from os import getenv
from loguru import logger

load_dotenv()


def _bool(key: str, default: str = "False") -> bool:
    return getenv(key, default).strip().lower() in ("1", "true", "yes", "on")


def _int(key: str, default: int) -> int:
    value = getenv(key)
    return int(value) if value else default


def _float(key: str, default: float) -> float:
    value = getenv(key)
    return float(value) if value else default


@dataclass(frozen=True)
class Config:

    API_ID: int = field(default_factory=lambda: _int("API_ID", 0))
    API_HASH: str = field(default_factory=lambda: getenv("API_HASH", ""))
    BOT_TOKEN: str = field(default_factory=lambda: getenv("BOT_TOKEN", ""))
    OWNER_ID: int = field(default_factory=lambda: _int("OWNER_ID", 0))


    MONGO_URL: str = field(default_factory=lambda: getenv("MONGO_URL", ""))


    MAX_ATTEMPTS: int = field(default_factory=lambda: _int("MAX_ATTEMPTS", 30))
    DEFAULT_DIFFICULTY: str = field(default_factory=lambda: getenv("DEFAULT_DIFFICULTY", "normal"))
    DEFAULT_LANG: str = field(default_factory=lambda: getenv("DEFAULT_LANG", "en"))
    LUCKY_ROUND_CHANCE: float = field(default_factory=lambda: _float("LUCKY_ROUND_CHANCE", 0.05))


    GROQ_API_KEY: str = field(default_factory=lambda: getenv("GROQ_API_KEY", ""))
    GROQ_MODEL: str = field(default_factory=lambda: getenv("GROQ_MODEL", "llama-3.3-70b-versatile"))
    GROQ_BASE_URL: str = field(default_factory=lambda: getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1"))
    WORD_GEN_BATCH_SIZE: int = field(default_factory=lambda: _int("WORD_GEN_BATCH_SIZE", 25))


    LOGGER_ID: int = field(default_factory=lambda: _int("LOGGER_ID", 0))
    SUPPORT_CHAT: str = field(default_factory=lambda: getenv("SUPPORT_CHAT", "https://t.me/THE_DRAGON_SUPPORT"))
    SUPPORT_CHANNEL: str = field(default_factory=lambda: getenv("SUPPORT_CHANNEL", "https://t.me/Senpai_Updates"))
    START_IMG: str = field(default_factory=lambda: getenv("START_IMG", "https://raw.githubusercontent.com/SenpaiLabs/Word-Guess-Bot/main/.github/banner.png"))
    PING_IMG: str = field(default_factory=lambda: getenv("PING_IMG", ""))

    def check(self) -> None:
        missing = [
            var
            for var in ["API_ID", "API_HASH", "BOT_TOKEN", "MONGO_URL", "LOGGER_ID", "OWNER_ID"]
            if not getattr(self, var)
        ]
        if missing:
            raise SystemExit(f"Missing required environment variables: {', '.join(missing)}")


config = Config()
config.check()


class InterceptHandler(logging.Handler):
    def emit(self, record):
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())

import sys
logger.remove()
logger.add(sys.stderr, level="INFO")

logging.basicConfig(handlers=[InterceptHandler()], level=logging.INFO, force=True)

for noisy in ("pyrogram", "pymongo", "apscheduler", "tzlocal", "asyncio"):
    logging.getLogger(noisy).setLevel(logging.WARNING)
