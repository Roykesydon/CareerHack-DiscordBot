import discord

from core.utils.config import CONFIG

"""
Bot response permission Control
"""


class AdminValidator:
    def __init__(self, administrator_manager):
        self._administrator_manager = administrator_manager

    def is_admin(self, user_id: str):
        return user_id in self._administrator_manager.get_admin_id_list()
