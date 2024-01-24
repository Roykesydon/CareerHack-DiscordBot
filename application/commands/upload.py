import discord
import requests
from discord import app_commands
from discord.ext import commands

from core.file_management.upload_file_manager import UploadFileManager
from core.utils.text_manager import TextManager
from main import channel_validator


class UploadFileCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def check_file_format(self, file_type) -> bool:
        return file_type in UploadFileManager.AVAILABLE_FILE_TYPE_DICT

    @app_commands.command(
        name="upload",
        description=TextManager.DEFAULT_LANG_DATA["commands"]["upload"]["description"],
    )
    async def upload_document(
        self,
        interaction,
        custom_file_name: str,
        attachment: discord.Attachment,
    ):
        text_manager = TextManager()
        LANG_DATA = text_manager.get_selected_language(str(interaction.channel_id))

        upload_file_manager = UploadFileManager()

        if not channel_validator.in_dm_or_enabled_channel(interaction.channel):
            await interaction.response.send_message(
                f"{LANG_DATA['permission']['dm-or-enabled-channel-only']}"
            )
            return

        """
        TODO: check document size
        """
        response = requests.get(attachment.url)

        """
        Check file format
        """
        if not self.check_file_format(attachment.content_type):
            await interaction.response.send_message(
                LANG_DATA["commands"]["upload"]["invalid-file-type"]
            )
            return

        async with interaction.channel.typing():
            await interaction.response.defer()

            upload_file_manager.upload_file(
                attachment=attachment,
                custom_file_name=custom_file_name,
                attachment_response=response,
                user_id=str(interaction.user.id),
            )

        return await interaction.followup.send(
            LANG_DATA["commands"]["upload"]["success"],
            ephemeral=True,
        )

    def cog_check(self, ctx):
        # check if the command is used in a channel that is enabled or in a DM
        return not isinstance(ctx.channel, discord.DMChannel)


async def setup(bot):
    await bot.add_cog(UploadFileCommand(bot))
