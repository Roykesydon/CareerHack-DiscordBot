import json

# open config.json
with open("config.json", "r", encoding="utf8") as f:
    CONFIG = json.load(f)
    bot_language = CONFIG["language"]

with open(f"lang/{bot_language}.json", "r", encoding="utf8") as f:
    LANG_DATA = json.load(f)
