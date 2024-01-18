import discord
from discord import app_commands
from discord.ext import commands

from core.text_manager import TextManager
from core.validator import Validator


class DescriptionCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="description",
        description=TextManager.DEFAULT_LANG_DATA["commands"]["description"][
            "description"
        ],
    )
    async def show_description(self, interaction):
        text_manager = TextManager()
        LANG_DATA = text_manager.get_selected_language(str(interaction.channel_id))

        if not Validator.in_dm_or_enabled_channel(interaction.channel):
            await interaction.response.send_message(
                f"{LANG_DATA['permission']['dm-or-enabled-channel-only']}"
            )
            return

        async with interaction.channel.typing():
            logo = discord.File("./assets/logo.png")
            description = LANG_DATA["description"]

            return await interaction.response.send_message(description, file=logo)


async def setup(bot):
    await bot.add_cog(DescriptionCommand(bot))
