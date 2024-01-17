import asyncio

import discord
from discord import SelectOption, app_commands, ui
from discord.ext import commands
from discord.ui import Button, View

from core.events.directly_chat import DirectlyChat
from core.text_manager import TextManager
from core.upload_file_manager import UploadFileManager
from core.validator import Validator


class DeleteUploadedFileSelectView(ui.View):
    def __init__(self, channel_id, user_id):
        super().__init__()

        # Add the dropdown to our view object
        self.add_item(DeleteUploadedFileSelect(channel_id, user_id))


class DeleteUploadedFileSelect(ui.Select):
    def __init__(self, channel_id, user_id):
        text_manager = TextManager()
        LANG_DATA = text_manager.get_selected_language(channel_id)

        options = []
        upload_file_manager = UploadFileManager()

        for file in upload_file_manager.get_available_file_list(user_id):
            options.append(SelectOption(label=file["file_name"], value=file["file_id"]))

        super().__init__(
            placeholder=LANG_DATA["commands"]["delete-uploaded-file"]["placeholder"],
            min_values=1,
            max_values=min(15, len(options)),
            options=options,
        )

    async def callback(self, interaction):
        selected_file = self.values[0]
        text_manager = TextManager()
        upload_file_manager = UploadFileManager()

        upload_file_manager.delete_file(selected_file)

        LANG_DATA = text_manager.get_selected_language(str(interaction.channel_id))

        await interaction.response.edit_message(view=None)

        await interaction.followup.send(
            LANG_DATA["commands"]["delete-uploaded-file"]["success"]
        )


class DeleteUploadedFileCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="delete-uploaded-file",
        description=TextManager.DEFAULT_LANG_DATA["commands"]["delete-uploaded-file"][
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
            view = DeleteUploadedFileSelectView(
                str(interaction.channel_id), str(interaction.user.id)
            )
            await interaction.response.send_message(
                LANG_DATA["commands"]["delete-uploaded-file"]["message"], view=view
            )


async def setup(bot):
    await bot.add_cog(DeleteUploadedFileCommand(bot))
