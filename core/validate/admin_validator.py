import discord

from core.utils.config import CONFIG

"""
Bot response permission Control
"""


class AdminValidator:
    def __init__(self):
        self._admin_username_list = CONFIG["admin_username_list"]

    def is_admin(self, username: str):
        return username in self._admin_username_list
