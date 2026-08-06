# Locales

Each `<lang>.json` file holds the bot's UI strings for one language.
Add a new language by copying `en.json`, translating the values (keep
the keys unchanged), and saving it as `<lang_code>.json` — e.g. `hi.json`.

Strings are loaded via `Senpai.core.lang.get_string(key, lang)`.
