import asyncio
import os

import discord
from discord import SelectOption, app_commands, ui
from discord.ext import commands
from discord.ui import Button, View

from core.events.directly_chat import DirectlyChat
from core.text_manager import TextManager
from core.upload_file_manager import UploadFileManager
from core.validator import Validator


class DownloadSelectView(ui.View):
    def __init__(self, channel_id, user_id):
        super().__init__()

        # Add the dropdown to our view object
        self.add_item(DownloadSelect(channel_id, user_id))


class DownloadSelect(ui.Select):
    def __init__(self, channel_id, user_id):
        text_manager = TextManager()
        LANG_DATA = text_manager.get_selected_language(channel_id)

        options = []
        upload_file_manager = UploadFileManager()

        for file in upload_file_manager.get_available_file_list(user_id):
            options.append(SelectOption(label=file["file_name"], value=file["file_id"]))

        super().__init__(
            placeholder=LANG_DATA["commands"]["download"]["placeholder"],
            min_values=1,
            max_values=min(15, len(options)),
            options=options,
        )

    async def callback(self, interaction):
        selected_file = self.values
        text_manager = TextManager()
        upload_file_manager = UploadFileManager()

        LANG_DATA = text_manager.get_selected_language(str(interaction.channel_id))

        available_file_list = upload_file_manager.get_available_file_list(
            str(interaction.user.id)
        )

        for file_id in selected_file:
            file_path = upload_file_manager.get_file_path(file_id)

            custom_file_name = ""
            for file in available_file_list:
                if file["file_id"] == file_id:
                    custom_file_name = file["file_name"]
                    break

            # send filename message with file
            await interaction.user.send(f"{custom_file_name}：")
            if file_path is not None:
                await interaction.user.send(file=discord.File(file_path))

        if interaction.message is not None:
            await interaction.message.delete()


class DownloadCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="download",
        description=TextManager.DEFAULT_LANG_DATA["commands"]["download"][
            "description"
        ],
    )
    async def ask_questions(self, interaction):
        text_manager = TextManager()
        LANG_DATA = text_manager.get_selected_language(str(interaction.channel_id))

        if not Validator.in_dm_or_enabled_channel(interaction.channel):
            await interaction.response.send_message(
                f"{LANG_DATA['permission']['dm-or-enabled-channel-only']}"
            )
            return

        async with interaction.channel.typing():
            view = DownloadSelectView(
                str(interaction.channel_id), str(interaction.user.id)
            )
            await interaction.response.send_message(
                LANG_DATA["commands"]["download"]["message"], view=view
            )


async def setup(bot):
    await bot.add_cog(DownloadCommand(bot))
