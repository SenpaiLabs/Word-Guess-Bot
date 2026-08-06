
from __future__ import annotations

from time import time

from motor.motor_asyncio import AsyncIOMotorClient

from config import config, logger
from Senpai.core.dir import WORDS_DIR
from Senpai.helpers._dataclass import Game, Group, Statistics, User, Word


class MongoDB:
    def __init__(self):
        self.client = AsyncIOMotorClient(config.MONGO_URL, serverSelectionTimeoutMS=12500)
        self.db = self.client[config.MONGO_DB_NAME]

        self.words = self.db.words
        self.games = self.db.games
        self.groups = self.db.groups
        self.users = self.db.users
        self.group_used_words = self.db.group_used_words
        self.leaderboards = self.db.leaderboards
        self.statistics = self.db.statistics
        self.cache = self.db.cache


        self._group_difficulty: dict[int, str] = {}

    async def connect(self) -> None:
        try:
            start = time()
            await self.client.admin.command("ping")
            logger.info(f"Database connection successful. ({time() - start:.2f}s)")
        except Exception as e:
            raise SystemExit(f"Database connection failed: {type(e).__name__}") from e

        await self._ensure_indexes()
        await self.import_words()

    async def close(self) -> None:
        self.client.close()

    async def _ensure_indexes(self) -> None:
        await self.words.create_index([("length", 1), ("difficulty", 1), ("enabled", 1)])
        await self.words.create_index("word", unique=True)
        await self.games.create_index([("chat_id", 1), ("status", 1)])
        await self.statistics.create_index([("chat_id", 1), ("total_points", -1)])


    async def import_words(self) -> None:
        marker = await self.cache.find_one({"_id": "words_imported"})
        if marker:
            return

        logger.info("Importing word lists into MongoDB (first run only)...")
        total = 0
        for length in (4, 5, 6):
            path = WORDS_DIR / f"{length}.txt"
            if not path.exists():
                logger.warning(f"Word list not found: {path}")
                continue

            words = [
                line.strip().lower()
                for line in path.read_text(encoding="utf-8").splitlines()
                if line.strip() and len(line.strip()) == length and line.strip().isalpha()
            ]
            if not words:
                continue

            docs = [Word(word=w, length=length).to_doc() for w in words]
            try:
                result = await self.words.insert_many(docs, ordered=False)
                total += len(result.inserted_ids)
            except Exception:
                pass

        await self.cache.update_one(
            {"_id": "words_imported"}, {"$set": {"count": total}}, upsert=True
        )
        logger.info(f"Word import complete. {total} words imported.")


    async def get_random_word(
        self, chat_id: int, length: int, difficulty: str
    ) -> Word | None:
        used_ids = await self._get_used_word_ids(chat_id, length)

        pipeline = [
            {
                "$match": {
                    "length": length,
                    "difficulty": difficulty,
                    "enabled": True,
                    "_id": {"$nin": list(used_ids)},
                }
            },
            {"$sample": {"size": 1}},
        ]
        doc = None
        async for d in self.words.aggregate(pipeline):
            doc = d
            break

        if not doc:
            await self.group_used_words.delete_one({"_id": f"{chat_id}:{length}"})
            async for d in self.words.aggregate(
                [
                    {"$match": {"length": length, "difficulty": difficulty, "enabled": True}},
                    {"$sample": {"size": 1}},
                ]
            ):
                doc = d
                break

        if not doc:
            return None

        await self._mark_word_used(chat_id, length, doc["_id"])
        await self.words.update_one({"_id": doc["_id"]}, {"$inc": {"times_used": 1}})
        return Word.from_doc(doc)

    async def _get_used_word_ids(self, chat_id: int, length: int) -> set:
        doc = await self.group_used_words.find_one({"_id": f"{chat_id}:{length}"})
        return set(doc.get("word_ids", [])) if doc else set()

    async def _mark_word_used(self, chat_id: int, length: int, word_id) -> None:
        await self.group_used_words.update_one(
            {"_id": f"{chat_id}:{length}"},
            {"$addToSet": {"word_ids": word_id}},
            upsert=True,
        )

    async def add_generated_words(self, words: list[str], length: int, difficulty: str) -> int:
        docs = [Word(word=w, length=length, difficulty=difficulty).to_doc() for w in words]
        if not docs:
            return 0
        try:
            result = await self.words.insert_many(docs, ordered=False)
            return len(result.inserted_ids)
        except Exception:
            return 0

    async def remaining_word_count(self, chat_id: int, length: int, difficulty: str) -> int:
        used_ids = await self._get_used_word_ids(chat_id, length)
        return await self.words.count_documents(
            {"length": length, "difficulty": difficulty, "enabled": True, "_id": {"$nin": list(used_ids)}}
        )

    async def is_valid_word(self, word: str) -> bool:
        doc = await self.words.find_one({"word": word.lower()})
        return doc is not None


    async def get_active_game(self, chat_id: int) -> Game | None:
        doc = await self.games.find_one({"chat_id": chat_id, "status": "active"})
        return Game.from_doc(doc) if doc else None

    async def save_game(self, game: Game) -> None:
        await self.games.update_one(
            {"chat_id": game.chat_id, "status": "active"},
            {"$set": game.to_doc()},
            upsert=True,
        )

    async def finish_game(self, game: Game) -> None:
        await self.games.update_one(
            {"chat_id": game.chat_id, "status": "active"},
            {"$set": game.to_doc()},
        )


    async def get_group_difficulty(self, chat_id: int) -> str:
        if chat_id in self._group_difficulty:
            return self._group_difficulty[chat_id]
        doc = await self.groups.find_one({"_id": chat_id})
        difficulty = doc["difficulty"] if doc else config.DEFAULT_DIFFICULTY
        self._group_difficulty[chat_id] = difficulty
        return difficulty

    async def set_group_difficulty(self, chat_id: int, difficulty: str, title: str = "") -> None:
        self._group_difficulty[chat_id] = difficulty
        await self.groups.update_one(
            {"_id": chat_id},
            {"$set": {"difficulty": difficulty, "title": title}},
            upsert=True,
        )

    async def register_group(self, group: Group) -> None:
        await self.groups.update_one(
            {"_id": group.chat_id},
            {"$setOnInsert": group.to_doc()},
            upsert=True,
        )


    async def register_user(self, user: User) -> None:
        await self.users.update_one(
            {"_id": user.user_id},
            {"$set": {"first_name": user.first_name, "username": user.username}},
            upsert=True,
        )


    async def get_statistics(self, user_id: int, chat_id: int) -> Statistics:
        doc = await self.statistics.find_one({"_id": f"{chat_id}:{user_id}"})
        return Statistics.from_doc(doc) if doc else Statistics(user_id=user_id, chat_id=chat_id)

    async def save_statistics(self, stats: Statistics) -> None:
        await self.statistics.update_one(
            {"_id": stats.to_doc()["_id"]}, {"$set": stats.to_doc()}, upsert=True
        )

    async def top_statistics(self, chat_id: int, limit: int = 10) -> list[Statistics]:
        cursor = self.statistics.find({"chat_id": chat_id}).sort("total_points", -1).limit(limit)
        return [Statistics.from_doc(doc) async for doc in cursor]

    async def get_users_map(self, user_ids: list[int]) -> dict:
        cursor = self.users.find({"_id": {"$in": user_ids}})
        return {doc["_id"]: User.from_doc(doc) async for doc in cursor}

    async def claim_daily_first_win(self, user_id: int) -> bool:
        from datetime import datetime, timezone

        day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        result = await self.cache.update_one(
            {"_id": f"daily_win:{day}:{user_id}"},
            {"$setOnInsert": {"claimed": True}},
            upsert=True,
        )
        return result.upserted_id is not None


db = MongoDB()
