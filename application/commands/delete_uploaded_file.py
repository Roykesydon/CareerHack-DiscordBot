import discord
from discord import SelectOption, app_commands, ui
from discord.ext import commands

from core.file_management.upload_file_manager import UploadFileManager
from core.utils.text_manager import TextManager
from main import admin_validator, channel_validator


class DeleteUploadedFileSelectView(ui.View):
    def __init__(self, channel_id, user_id, username):
        super().__init__()

        # Add the dropdown to our view object
        self.add_item(DeleteUploadedFileSelect(channel_id, user_id, username))


class DeleteUploadedFileSelect(ui.Select):
    def __init__(self, channel_id, user_id, username):
        text_manager = TextManager()
        LANG_DATA = text_manager.get_selected_language(channel_id)

        options = []
        upload_file_manager = UploadFileManager()

        for file in upload_file_manager.get_available_file_list(user_id):
            if not admin_validator.is_admin(user_id) and file["file_scope"] == "shared":
                continue

            options.append(
                SelectOption(
                    label=file["file_name"], emoji=file["emoji"], value=file["file_id"]
                )
            )

        super().__init__(
            placeholder=LANG_DATA["commands"]["delete-uploaded-file"]["placeholder"],
            min_values=1,
            max_values=min(15, len(options)),
            options=options,
        )

    async def callback(self, interaction):
        selected_file = self.values
        text_manager = TextManager()
        upload_file_manager = UploadFileManager()

        upload_file_manager.delete_file(selected_file)

        LANG_DATA = text_manager.get_selected_language(str(interaction.channel_id))

        if interaction.message is not None:
            await interaction.message.delete()

        if isinstance(interaction.channel, discord.channel.TextChannel) or isinstance(
            interaction.channel, discord.channel.DMChannel
        ):
            await interaction.channel.send(
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

        upload_file_manager = UploadFileManager()

        if not channel_validator.in_dm_or_enabled_channel(interaction.channel):
            await interaction.response.send_message(
                f"{LANG_DATA['permission']['dm-or-enabled-channel-only']}"
            )
            return

        private_only = not admin_validator.is_admin(str(interaction.user.id))
        if (
            len(
                upload_file_manager.get_available_file_list(
                    str(interaction.user.id), private_only=private_only
                )
            )
            == 0
        ):
            await interaction.response.send_message(
                f"{LANG_DATA['commands']['download']['no-file']}"
            )
            return

        async with interaction.channel.typing():
            view = DeleteUploadedFileSelectView(
                str(interaction.channel_id),
                str(interaction.user.id),
                str(interaction.user.name),
            )
            await interaction.response.send_message(
                LANG_DATA["commands"]["delete-uploaded-file"]["message"], view=view
            )


async def setup(bot):
    await bot.add_cog(DeleteUploadedFileCommand(bot))
