

import asyncio
import json
import re

from openai import AsyncOpenAI

from config import config
from loguru import logger
from Senpai.core.mongo import db

class AIWordGenerator:
    REPLENISH_THRESHOLD = 5
    DIFFICULTY_HINT = {
        "normal": "common, everyday English words that most people would easily recognize",
        "medium": "moderately common English words — a step up from basic everyday vocabulary",
        "hard": "challenging but still valid dictionary English words (no obscure jargon or archaic spellings)",
    }

    def __init__(self):
        self._client: AsyncOpenAI | None = None
        self._in_progress: set[tuple[int, str]] = set()

    def _get_client(self) -> AsyncOpenAI:
        if self._client is None:
            self._client = AsyncOpenAI(api_key=config.GROQ_API_KEY, base_url=config.GROQ_BASE_URL)
        return self._client

    async def generate_words(self, length: int, difficulty: str, count: int) -> list[str]:
        if not config.GROQ_API_KEY:
            logger.warning("GROQ_API_KEY not set — skipping AI word generation.")
            return []

        hint = self.DIFFICULTY_HINT.get(difficulty, self.DIFFICULTY_HINT["normal"])
        prompt = (
            f"Generate exactly {count} valid, real English dictionary words, each exactly "
            f"{length} letters long, all lowercase, no proper nouns, no repeats. "
            f"They should be {hint}. "
            'Respond ONLY with a JSON array of strings, nothing else — no markdown, no '
            'explanation. Example format: ["abcde", "fghij"]'
        )

        try:
            response = await self._get_client().chat.completions.create(
                model=config.GROQ_MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.9,
                max_tokens=800,
            )
            raw = (response.choices[0].message.content or "").strip()
            raw = re.sub(r"^```(json)?|```$", "", raw, flags=re.MULTILINE).strip()
            words = json.loads(raw)
        except Exception as e:
            logger.error(f"AI word generation request failed: {type(e).__name__}: {e}")
            return []

        valid, seen = [], set()
        for w in words if isinstance(words, list) else []:
            if not isinstance(w, str):
                continue
            w = w.strip().lower()
            if len(w) == length and w.isalpha() and w not in seen:
                valid.append(w)
                seen.add(w)

        return valid

    async def replenish(self, length: int, difficulty: str) -> None:
        key = (length, difficulty)
        if key in self._in_progress:
            return

        self._in_progress.add(key)
        try:
            words = await self.generate_words(length, difficulty, config.WORD_GEN_BATCH_SIZE)
            if not words:
                return
            inserted = await db.add_generated_words(words, length, difficulty)
            logger.info(f"AI word generation: +{inserted} new {length}-letter ({difficulty}) words.")
        finally:
            self._in_progress.discard(key)

    async def maybe_replenish(self, chat_id: int, length: int, difficulty: str) -> None:
        remaining = await db.remaining_word_count(chat_id, length, difficulty)
        if remaining <= self.REPLENISH_THRESHOLD:
            asyncio.create_task(self.replenish(length, difficulty))


word_gen = AIWordGenerator()
