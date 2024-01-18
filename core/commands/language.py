import asyncio

import discord
from discord import SelectOption, app_commands, ui
from discord.ext import commands
from discord.ui import Button, View

from core.text_manager import TextManager
from core.validator import Validator


class LanguageSelectView(ui.View):
    def __init__(self, channel_id):
        super().__init__()

        # Add the dropdown to our view object
        self.add_item(LanguageSelect(channel_id))


class LanguageSelect(ui.Select):
    def __init__(self, channel_id):
        text_manager = TextManager()
        options = []

        for lang in text_manager.get_language_list():
            options.append(SelectOption(label=lang["label"], value=lang["value"]))

        text_manager = TextManager()
        LANG_DATA = text_manager.get_selected_language(channel_id)

        super().__init__(
            placeholder=LANG_DATA["commands"]["language"]["placeholder"],
            min_values=1,
            max_values=1,
            options=options,
        )

    async def callback(self, interaction):
        # select new language
        selected_language = self.values[0]
        text_manager = TextManager()
        text_manager.select_language(str(interaction.channel_id), selected_language)

        LANG_DATA = text_manager.get_selected_language(str(interaction.channel_id))

        self.disabled = True
        await interaction.response.edit_message(view=self.view)

        # Here you can add code to update the user's language preference
        await interaction.followup.send(
            LANG_DATA["commands"]["language"]["success"],
        )


class LanguageCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="language",
        description=TextManager.DEFAULT_LANG_DATA["commands"]["language"][
            "description"
        ],
    )
    async def change_language(self, interaction):
        text_manager = TextManager()
        LANG_DATA = text_manager.get_selected_language(str(interaction.channel_id))

        async with interaction.channel.typing():
            view = LanguageSelectView(str(interaction.channel_id))
            await interaction.response.send_message(
                LANG_DATA["commands"]["language"]["message"], view=view
            )


async def setup(bot):
    await bot.add_cog(LanguageCommand(bot))
