import discord

from core.config import CONFIG


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
            for field_name, field_value in self._field.items():
                embed.add_field(name=field_name, value=field_value, inline=False)

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

    def get_field(self) -> dict:
        return self._field

    def set_field(self, field: dict):
        self._field = field

    def get_img(self) -> discord.File:
        return self._img

    def set_img(self, img: discord.File):
        self._img = img
