

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from dotenv import load_dotenv
from os import getenv

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
    MONGO_DB_NAME: str = field(default_factory=lambda: getenv("MONGO_DB_NAME", "WordGuessBot"))


    MAX_ATTEMPTS: int = field(default_factory=lambda: _int("MAX_ATTEMPTS", 30))
    DEFAULT_DIFFICULTY: str = field(default_factory=lambda: getenv("DEFAULT_DIFFICULTY", "normal"))
    LUCKY_ROUND_CHANCE: float = field(default_factory=lambda: _float("LUCKY_ROUND_CHANCE", 0.05))


    GROQ_API_KEY: str = field(default_factory=lambda: getenv("GROQ_API_KEY", ""))
    GROQ_MODEL: str = field(default_factory=lambda: getenv("GROQ_MODEL", "llama-3.3-70b-versatile"))
    GROQ_BASE_URL: str = field(default_factory=lambda: getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1"))
    WORD_GEN_BATCH_SIZE: int = field(default_factory=lambda: _int("WORD_GEN_BATCH_SIZE", 25))


    LOG_GROUP_ID: int = field(default_factory=lambda: _int("LOG_GROUP_ID", 0))
    SUPPORT_CHAT: str = field(default_factory=lambda: getenv("SUPPORT_CHAT", ""))
    START_IMG: str = field(default_factory=lambda: getenv("START_IMG", "https://raw.githubusercontent.com/SenpaiLabs/Word-Guess-Bot/main/.github/banner.png"))

    def validate(self) -> None:
        required = {
            "API_ID": self.API_ID,
            "API_HASH": self.API_HASH,
            "BOT_TOKEN": self.BOT_TOKEN,
            "MONGO_URL": self.MONGO_URL,
        }
        missing = [key for key, value in required.items() if not value]
        if missing:
            raise SystemExit(f"Missing required environment variables: {', '.join(missing)}")


config = Config()


def setup_logging() -> logging.Logger:
    logging.basicConfig(
        level=logging.INFO,
        format="[%(asctime)s - %(levelname)s] - %(name)s: %(message)s",
        datefmt="%d-%b-%y %H:%M:%S",
        handlers=[logging.FileHandler("log.txt"), logging.StreamHandler()],
    )

    for noisy in ("pyrogram", "pymongo", "apscheduler"):
        logging.getLogger(noisy).setLevel(logging.WARNING)
    return logging.getLogger("word-guess-bot")


logger = setup_logging()
