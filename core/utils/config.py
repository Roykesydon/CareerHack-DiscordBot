import json

# open config.json
with open("config.json", "r", encoding="utf8") as f:
    CONFIG = json.load(f)


def update_config():
    global CONFIG
    with open("config.json", "w", encoding="utf8") as f:
        json.dump(CONFIG, f, indent=4, ensure_ascii=False)
