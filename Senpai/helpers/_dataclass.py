from __future__ import annotations

from dataclasses import dataclass, field
from time import time


@dataclass
class Word:
    word: str
    length: int
    difficulty: str = "normal"  # normal | medium | hard
    times_used: int = 0
    enabled: bool = True

    def to_doc(self) -> dict:
        return {
            "word": self.word,
            "length": self.length,
            "difficulty": self.difficulty,
            "times_used": self.times_used,
            "enabled": self.enabled,
        }

    @classmethod
    def from_doc(cls, doc: dict) -> "Word":
        return cls(
            word=doc["word"],
            length=doc["length"],
            difficulty=doc.get("difficulty", "normal"),
            times_used=doc.get("times_used", 0),
            enabled=doc.get("enabled", True),
        )


@dataclass
class GuessResult:
    guess: str
    pattern: str  # e.g. "🟩🟨🟥🟥🟩"
    user_id: int
    timestamp: float = field(default_factory=time)

    def to_doc(self) -> dict:
        return {
            "guess": self.guess,
            "pattern": self.pattern,
            "user_id": self.user_id,
            "timestamp": self.timestamp,
        }

    @classmethod
    def from_doc(cls, doc: dict) -> "GuessResult":
        return cls(
            guess=doc["guess"],
            pattern=doc["pattern"],
            user_id=doc["user_id"],
            timestamp=doc.get("timestamp", time()),
        )


@dataclass
class Game:
    chat_id: int
    word: str
    length: int
    difficulty: str
    started_by: int
    message_id: int | None = None
    status: str = "active"  # active | won | lost | ended
    guesses: list[GuessResult] = field(default_factory=list)
    started_at: float = field(default_factory=time)
    ended_at: float | None = None
    winner_id: int | None = None
    lucky_round: bool = False

    @property
    def attempts(self) -> int:
        return len(self.guesses)

    @property
    def elapsed_seconds(self) -> int:
        end = self.ended_at or time()
        return int(end - self.started_at)

    def to_doc(self) -> dict:
        return {
            "chat_id": self.chat_id,
            "word": self.word,
            "length": self.length,
            "difficulty": self.difficulty,
            "started_by": self.started_by,
            "message_id": self.message_id,
            "status": self.status,
            "guesses": [g.to_doc() for g in self.guesses],
            "started_at": self.started_at,
            "ended_at": self.ended_at,
            "winner_id": self.winner_id,
            "lucky_round": self.lucky_round,
        }

    @classmethod
    def from_doc(cls, doc: dict) -> "Game":
        return cls(
            chat_id=doc["chat_id"],
            word=doc["word"],
            length=doc["length"],
            difficulty=doc["difficulty"],
            started_by=doc["started_by"],
            message_id=doc.get("message_id"),
            status=doc.get("status", "active"),
            guesses=[GuessResult.from_doc(g) for g in doc.get("guesses", [])],
            started_at=doc.get("started_at", time()),
            ended_at=doc.get("ended_at"),
            winner_id=doc.get("winner_id"),
            lucky_round=doc.get("lucky_round", False),
        )


@dataclass
class Group:
    chat_id: int
    title: str = ""
    difficulty: str = "normal"

    def to_doc(self) -> dict:
        return {"_id": self.chat_id, "title": self.title, "difficulty": self.difficulty}

    @classmethod
    def from_doc(cls, doc: dict) -> "Group":
        return cls(
            chat_id=doc["_id"],
            title=doc.get("title", ""),
            difficulty=doc.get("difficulty", "normal"),
        )


@dataclass
class User:
    user_id: int
    first_name: str = ""
    username: str | None = None

    def to_doc(self) -> dict:
        return {"_id": self.user_id, "first_name": self.first_name, "username": self.username}

    @classmethod
    def from_doc(cls, doc: dict) -> "User":
        return cls(
            user_id=doc["_id"],
            first_name=doc.get("first_name", ""),
            username=doc.get("username"),
        )


@dataclass
class Statistics:
    """One doc per (user_id, chat_id). chat_id = 0 is the GLOBAL scope."""

    user_id: int
    chat_id: int
    games_played: int = 0
    games_won: int = 0
    games_lost: int = 0
    total_points: int = 0
    current_streak: int = 0
    highest_streak: int = 0
    fastest_solve: int | None = None
    perfect_guesses: int = 0
    total_guesses: int = 0
    hard_wins: int = 0
    badges: list[str] = field(default_factory=list)

    @property
    def average_attempts(self) -> float:
        if not self.games_played:
            return 0.0
        return round(self.total_guesses / self.games_played, 2)

    def to_doc(self) -> dict:
        return {
            "_id": f"{self.chat_id}:{self.user_id}",
            "user_id": self.user_id,
            "chat_id": self.chat_id,
            "games_played": self.games_played,
            "games_won": self.games_won,
            "games_lost": self.games_lost,
            "total_points": self.total_points,
            "current_streak": self.current_streak,
            "highest_streak": self.highest_streak,
            "fastest_solve": self.fastest_solve,
            "perfect_guesses": self.perfect_guesses,
            "total_guesses": self.total_guesses,
            "hard_wins": self.hard_wins,
            "badges": self.badges,
        }

    @classmethod
    def from_doc(cls, doc: dict) -> "Statistics":
        return cls(
            user_id=doc["user_id"],
            chat_id=doc["chat_id"],
            games_played=doc.get("games_played", 0),
            games_won=doc.get("games_won", 0),
            games_lost=doc.get("games_lost", 0),
            total_points=doc.get("total_points", 0),
            current_streak=doc.get("current_streak", 0),
            highest_streak=doc.get("highest_streak", 0),
            fastest_solve=doc.get("fastest_solve"),
            perfect_guesses=doc.get("perfect_guesses", 0),
            total_guesses=doc.get("total_guesses", 0),
            hard_wins=doc.get("hard_wins", 0),
            badges=doc.get("badges", []),
        )
