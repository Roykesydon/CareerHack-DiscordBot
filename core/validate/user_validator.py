import discord

from core.discord_api import DiscordAPI

"""
Bot response permission Control
"""


class UserValidator:
    def __init__(self):
        self._discord_api = DiscordAPI()

    def is_user_id_valid(self, user_id: str):
        try:
            user_info = self._discord_api.get_user_info(user_id)
            if "code" in user_info:
                return False
            if "username" not in user_info:
                return False
            return True
        except:
            return False
