import discord
from core.config import LANG_DATA
from discord import app_commands
from discord.ext import commands


class DescriptionCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="description",
        description=LANG_DATA["commands"]["description"]["description"],
    )
    async def show_description(self, interaction):
        async with interaction.channel.typing():
            # send logo
            logo = discord.File("./assets/logo.png")
            await interaction.channel.send(file=logo)

            # send description
            description = LANG_DATA["description"]
            await interaction.response.send_message(description)


async def setup(bot):
    await bot.add_cog(DescriptionCommand(bot))
