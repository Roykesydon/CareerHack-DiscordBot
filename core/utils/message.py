from typing import Union

import discord

from core.utils.config import CONFIG


class Message:
    def __init__(self, text="", field=None, img=None):
        self._text = text
        self._field = field
        self._img = img

    def get_embed_format(
        self, title: str, color: str = CONFIG["primary_color"]
    ) -> discord.Embed:
        # set embed color
        color_int = int(color.replace("#", ""), 16)

        embed = discord.Embed(
            title=title,
            color=color_int,
        )

        # Add message content
        if self._text:
            embed.description = self.get_text()

        # Add embed fields
        if self._field:
            for index, (field_name, field_value) in enumerate(self._field.items()):
                value = field_value

                if index != len(self._field) - 1:
                    value = value + "\u200b"

                embed.add_field(name=field_name, value=value, inline=False)

        # Add image if available
        if self._img:
            if isinstance(self._img, discord.File):
                embed.set_thumbnail(url=f"attachment://{self._img.filename}")
            else:
                embed.set_thumbnail(url=str(self._img))

        return embed

    # getters and setters
    def get_text(self) -> str:
        return self._text

    def set_text(self, text: str):
        self._text = text

    def get_field(self) -> Union[dict, None]:
        return self._field

    def set_field(self, field: dict):
        self._field = field

    def get_img(self) -> Union[discord.File, None]:
        return self._img

    def set_img(self, img: discord.File):
        self._img = img
