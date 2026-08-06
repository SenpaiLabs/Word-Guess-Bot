# Word Guess Bot

A production-ready, open-source Telegram Word Guess (Wordle-style) bot. Fully
async, modular, and built to scale across thousands of groups.

## Tech Stack

- Python 3.12+
- Pyrogram — Telegram client
- Motor — async MongoDB driver
- APScheduler — background scheduling
- Groq (OpenAI-compatible API) — background word generation
- Docker & Docker Compose

## Project Structure

```
word-guess-bot/
├── Senpai/                    # Main package (AnonXMusic-style layout)
│   ├── __init__.py             # Creates the Pyrogram `app` (via core.bot) + scheduler
│   ├── main.py                 # Entrypoint — run via `python3 -m Senpai.main`
│   │
│   ├── core/
│   │   ├── bot.py               # Pyrogram Client instance
│   │   ├── dir.py                # Path constants (WORDS_DIR, LOCALES_DIR)
│   │   ├── lang.py               # Locale (en.json etc.) loader
│   │   └── mongo.py              # Motor/MongoDB access layer
│   │
│   ├── helpers/                 # Flat, no sub-folders — same convention as anony/helpers
│   │   ├── _admins.py            # Admin-only Pyrogram filter
│   │   ├── _badges.py            # Badge computation
│   │   ├── _board.py             # Board / result rendering
│   │   ├── _dataclass.py         # Word, Game, GuessResult, Group, User, Statistics
│   │   ├── _evaluator.py         # Guess evaluation logic
│   │   ├── _game_engine.py       # Game lifecycle engine
│   │   ├── _inline.py            # Reserved for future inline-keyboard UI
│   │   ├── _scoring.py           # Score calculation
│   │   ├── _stats.py             # Player/group statistics
│   │   ├── _utilities.py         # Mentions, time formatting
│   │   └── _word_generator.py    # AI (Groq) word replenishment
│   │
│   ├── locales/                 # UI strings — add more languages here
│   │   ├── README.md
│   │   └── en.json
│   │
│   ├── plugins/                 # Telegram command & message handlers (Pyrogram plugins)
│   │   ├── start.py
│   │   ├── game.py
│   │   ├── guess.py
│   │   ├── leaderboard.py
│   │   └── mystats.py
│   │
│   └── words/                    # Starter word lists (4.txt, 5.txt, 6.txt)
│
├── config.py                    # Env-driven settings (loaded from outside Senpai)
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── setup                         # ./setup — installs dependencies
├── start                         # ./start — runs the bot
├── .env.example
└── README.md
```

## Setup

1. **Get credentials:**
   - Telegram `API_ID` / `API_HASH` from [my.telegram.org](https://my.telegram.org)
   - `BOT_TOKEN` from [@BotFather](https://t.me/BotFather)
   - A MongoDB connection string (Atlas free tier works fine)
   - A [Groq API key](https://console.groq.com) (optional — bot works without it,
     just without AI word replenishment)

2. **Configure:**
   ```bash
   cp .env.example .env
   # fill in the values
   ```

3. **Run with Docker:**
   ```bash
   docker compose up -d --build
   ```

   Or without Docker:
   ```bash
   ./setup
   ./start
   ```

On first run, the bot imports `words/4.txt`, `5.txt`, `6.txt` into MongoDB
automatically (one-time — subsequent runs skip this and use the DB only).

> **Note on the starter word lists:** they're pulled from a large general-purpose
> English dictionary corpus and include some fairly obscure/archaic words. For
> a better play experience, consider curating them down to more common words
> before your first import (the import only happens once, so edit the `.txt`
> files *before* first boot, or clear the `words` collection + the
> `words_imported` cache marker to re-import).

## Commands

| Command | Description |
|---|---|
| `/start` | Bot intro |
| `/new` | Start a game — random length (4/5/6, equal probability) |
| `/new4` / `/new5` / `/new6` | Start a game with a specific word length |
| `/end` | *(admin)* Reveal the answer and end the current game |
| `/game` | Show current game info (mode, attempts, starter, elapsed time, difficulty) |
| `/setmode normal\|medium\|hard` | *(admin)* Set this group's difficulty for future games |
| `/leaderboard` | Top 10 players in this group |
| `/gleaderboard` | Top 10 players across all groups |
| `/mystats` | Your personal stats (this group + global) |

Only one game can run per group at a time.

## Game Rules

- **Attempts:** 30 guesses max per game.
- **Evaluation:** local Wordle logic, no AI — 🟩 correct spot, 🟨 wrong spot, 🟥 not in word.
  Correctly handles duplicate letters (two-pass algorithm).
- **UI:** one message per game, edited in place after every guess. Player
  guess messages are deleted automatically if the bot has permission.
- **Word history:** each group gets its own no-repeat history per word
  length. Once every word of a mode is exhausted, the history resets and
  the AI background generator (if configured) tops up the pool.

## Scoring

| Component | Value |
|---|---|
| Base | `31 - attempts` (guess #1 → 30 pts, guess #30 → 1 pt) |
| Hard Mode bonus | 4L +0 / 5L +2 / 6L +5 |
| Win streak bonus | 3 wins +3, 5 wins +5, 10 wins +10 (highest threshold met, not stacked) |
| Speed bonus | ≤2 min +5, ≤5 min +2 |
| Perfect guess (1st try) | +10 |
| Daily first win | +5 (once per user per UTC day) |
| Lucky Round | all of the above **doubled** (random chance, configurable via `LUCKY_ROUND_CHANCE`) |

## Badges

| Badge | Condition |
|---|---|
| 👑 Top Player | Rank #1 on a leaderboard — dynamic, shown at render time only |
| 🔥 Win Streak | Current streak ≥ 5 |
| ⚡ Speed Master | Fastest solve ≤ 60s |
| 💎 Hard Mode Master | 10+ wins on hard difficulty |
| 🎯 Perfect Guesser | 5+ first-try wins |

## Database Collections

| Collection | Purpose |
|---|---|
| `words` | Word pool (imported + AI-generated) |
| `games` | Active + historical game state, one active doc per chat |
| `groups` | Per-group settings (difficulty, title) |
| `users` | Cached user profiles (id, name, username) — no live API calls needed for display |
| `group_used_words` | Per-chat, per-length no-repeat history |
| `statistics` | Per-user stats, one doc per (chat_id, user_id); `chat_id=0` = global scope |
| `cache` | Misc singleton docs (import marker, daily-win claims) |

## Architecture Notes

- **Game Engine vs Plugins:** `Senpai/helpers/_game_engine.py`, `_board.py`, and
  `_evaluator.py` never import Pyrogram — pure logic that could be unit-tested
  or reused outside Telegram entirely. `Senpai/plugins/` is the thin
  Telegram-facing layer.
- **Mentions without live API calls:** user display names are stored locally
  (`users` collection) whenever a user interacts with the bot, and mention
  links are built manually (`tg://user?id=`) rather than via `get_users()`.
  This avoids `PEER_ID_INVALID` errors for users the bot hasn't privately
  messaged — a common gotcha with Pyrogram bots resolving arbitrary group
  members.
- **AI word generation** only fires when a mode's pool is low (not per-game),
  runs as a background `asyncio.create_task` so it never blocks gameplay, and
  every generated word is validated (length + alphabetic) before storage —
  the AI is never trusted blindly, and it's never used for guess evaluation.

## Extending

The structure is set up to make these straightforward additions:

- 7/8-letter modes — add to `GameEngine.VALID_LENGTHS`, drop in a word list
- Multi-language word packs — add a `language` field to the `Word` model
- Daily challenges / seasonal events — new APScheduler jobs + a `challenges` collection
- REST API / web dashboard — the `services/` layer already has no Telegram
  dependency, so it can be reused behind a FastAPI layer
- Discord support — same story: `engine/` and `services/` are transport-agnostic

## License

MIT
