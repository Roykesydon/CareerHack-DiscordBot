import discord

from core.config import CONFIG


class Message:
    def __init__(self, text=""):
        self._text = text

    def get_embed_format(
        self, title: str, color: str = CONFIG["primary_color"]
    ) -> discord.Embed:
        # set embed color
        color_int = int(color.replace("#", ""), 16)

        # send commands list
        return discord.Embed(
            title=title,
            description=self.get_text(),
            color=color_int,
        )

    # getters and setters

    def get_text(self) -> str:
        return self._text

    def set_text(self, text: str):
        self._text = text
