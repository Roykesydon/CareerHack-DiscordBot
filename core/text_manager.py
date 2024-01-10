import json
from pathlib import Path

from core.config import CONFIG

_bot_language = CONFIG["language"]
with open(f"lang/{_bot_language}.json", "r", encoding="utf8") as f:
    _DEFAULT_LANG_DATA = json.load(f)

"""
Manage all fixed text in response or ui
"""


class TextManager:
    _channel_session = {}
    _language_text = {}
    _langauge_list = []

    DEFAULT_LANG_DATA = _DEFAULT_LANG_DATA

    @staticmethod
    def _load_language_text():
        TextManager._langauge_list = []
        # read all text file under lang folder
        for path in Path("./lang").glob("*.json"):
            with open(path, "r", encoding="utf8") as f:
                # parse json file
                text = json.load(f)
                TextManager._langauge_list.append(
                    {"label": text["label"], "value": text["value"]}
                )

        for lang in TextManager._langauge_list:
            with open(f"lang/{lang['value']}.json", "r", encoding="utf8") as f:
                TextManager._language_text[lang["value"]] = json.load(f)

    def get_language_list(self):
        if len(TextManager._langauge_list) == 0:
            TextManager._load_language_text()
        return TextManager._langauge_list

    """
    get selected language text as dict
    structure like json file in lang folder
    """

    def get_selected_language(self, channel_id: str) -> dict:
        if channel_id not in TextManager._channel_session:
            TextManager._channel_session[channel_id] = "zh-tw"

        selected_language = TextManager._channel_session[channel_id]

        # check if language text is loaded
        if selected_language not in TextManager._language_text:
            TextManager._load_language_text()

        return TextManager._language_text[selected_language]

    def select_language(self, channel_id, new_lang):
        TextManager._channel_session[channel_id] = new_lang
