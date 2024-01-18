import time

import discord
import requests
from discord import SelectOption, app_commands, ui
from discord.ext import commands

from core.utils.config import CONFIG
from core.utils.database import mongo_database
from core.utils.text_manager import TextManager
from core.validate.channel_validator import ChannelValidator
from main import hacker_rank_tools


class UploadFileCommand(commands.Cog):
    AVAILABLE_FILE_TYPE_DICT = {
        "text/plain": "txt",
        "application/pdf": "pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
    }

    def __init__(self, bot):
        self.bot = bot

    def check_file_format(self, file_type) -> bool:
        return file_type in UploadFileCommand.AVAILABLE_FILE_TYPE_DICT

    @app_commands.command(
        name="upload",
        description=TextManager.DEFAULT_LANG_DATA["commands"]["upload"]["description"],
    )
    @app_commands.choices(
        file_scope=[
            app_commands.Choice(name="共享文件", value="shared"),
            app_commands.Choice(name="私人使用", value="private"),
        ]
    )
    async def upload_document(
        self,
        interaction,
        file_scope: str,
        custom_file_name: str,
        attachment: discord.Attachment,
    ):
        text_manager = TextManager()
        LANG_DATA = text_manager.get_selected_language(str(interaction.channel_id))

        if not ChannelValidator.in_dm_or_enabled_channel(interaction.channel):
            await interaction.response.send_message(
                f"{LANG_DATA['permission']['dm-or-enabled-channel-only']}"
            )
            return

        async with interaction.channel.typing():
            """
            TODO: check document type, size
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

            await interaction.response.defer()

            if attachment.content_type is None:
                attachment.content_type = "text/plain"

            file_name = attachment.filename
            insert_data = {
                "file_name": file_name,
                "custom_file_name": custom_file_name
                if custom_file_name != ""
                else file_name,
                "file_type": attachment.content_type,
                "file_url": attachment.url,
                "file_time": int(time.time()),
                "file_scope": file_scope,
                "user_id": str(interaction.user.id),
                "filename_extension": UploadFileCommand.AVAILABLE_FILE_TYPE_DICT[
                    attachment.content_type
                ],
            }
            mongo_database["UserUploadFile"].insert_one(insert_data)

            # get document id from mongo as file name
            # save file to local storage
            file = mongo_database["UserUploadFile"].find_one(insert_data)
            if file is not None:
                file_name = str(file["_id"])

            if attachment.content_type is not None:
                with open(
                    f"{CONFIG['storage_path']}/{file_name}.{UploadFileCommand.AVAILABLE_FILE_TYPE_DICT[attachment.content_type]}",
                    "wb",
                ) as file:
                    file.write(response.content)

                file_paths = [
                    f"{CONFIG['storage_path']}/{file_name}.{UploadFileCommand.AVAILABLE_FILE_TYPE_DICT[attachment.content_type]}"
                ]
                hacker_rank_tools.add_documents_to_vdb(file_paths)

        return await interaction.followup.send(
            LANG_DATA["commands"]["upload"]["success"]
        )

    def cog_check(self, ctx):
        # check if the command is used in a channel that is enabled or in a DM
        return not isinstance(ctx.channel, discord.DMChannel)


async def setup(bot):
    await bot.add_cog(UploadFileCommand(bot))
