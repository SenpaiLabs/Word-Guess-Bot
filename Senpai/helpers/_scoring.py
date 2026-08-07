

from dataclasses import dataclass

from config import config

HARD_MODE_BONUS = {4: 0, 5: 2, 6: 5}
STREAK_BONUSES = {3: 3, 5: 5, 10: 10}


def base_points(attempts: int) -> int:

    return max(0, config.MAX_ATTEMPTS - attempts + 1)


def hard_mode_bonus(difficulty: str, length: int) -> int:
    if difficulty != "hard":
        return 0
    return HARD_MODE_BONUS.get(length, 0)


def streak_bonus(streak_after_this_win: int) -> int:
    bonus = 0
    for threshold, value in STREAK_BONUSES.items():
        if streak_after_this_win >= threshold:
            bonus = value
    return bonus


def speed_bonus(elapsed_seconds: int) -> int:
    if elapsed_seconds <= 120:
        return 5
    if elapsed_seconds <= 300:
        return 2
    return 0


def perfect_guess_bonus(attempts: int) -> int:
    return 10 if attempts == 1 else 0


@dataclass
class ScoreBreakdown:
    base: int = 0
    hard_mode: int = 0
    streak: int = 0
    speed: int = 0
    perfect: int = 0
    daily_first_win: int = 0
    lucky_round: bool = False

    @property
    def subtotal(self) -> int:
        return self.base + self.hard_mode + self.streak + self.speed + self.perfect + self.daily_first_win

    @property
    def total(self) -> int:
        return self.subtotal * 2 if self.lucky_round else self.subtotal

    def as_lines(self) -> list[str]:
        lines = [f"Base: +{self.base}"]
        if self.hard_mode:
            lines.append(f"Hard Mode: +{self.hard_mode}")
        if self.streak:
            lines.append(f"Win Streak: +{self.streak}")
        if self.speed:
            lines.append(f"Speed: +{self.speed}")
        if self.perfect:
            lines.append(f"Perfect Guess: +{self.perfect}")
        if self.daily_first_win:
            lines.append(f"Daily First Win: +{self.daily_first_win}")
        if self.lucky_round:
            lines.append(f"🍀 Lucky Round: x2 (subtotal {self.subtotal} → {self.total})")
        return lines


def calculate_score(
    *,
    attempts: int,
    difficulty: str,
    length: int,
    streak_after_this_win: int,
    elapsed_seconds: int,
    daily_first_win: bool,
    lucky_round: bool,
) -> ScoreBreakdown:
    return ScoreBreakdown(
        base=base_points(attempts),
        hard_mode=hard_mode_bonus(difficulty, length),
        streak=streak_bonus(streak_after_this_win),
        speed=speed_bonus(elapsed_seconds),
        perfect=perfect_guess_bonus(attempts),
        daily_first_win=5 if daily_first_win else 0,
        lucky_round=lucky_round,
    )
