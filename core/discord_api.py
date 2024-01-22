import requests

from core.utils.config import CONFIG


class DiscordAPI:
    def get_user_info(self, user_id: str):
        api_url = f"https://discord.com/api/v10/users/{user_id}"
        headers = {
            "Authorization": f"Bot {CONFIG['discord']['token']}",
        }
        response = requests.get(api_url, headers=headers)
        return response.json()

    def get_user_avatar(self, user_id: str, avatar_id: str):
        api_url = f"https://cdn.discordapp.com/avatars/{user_id}/{avatar_id}"
        return api_url
