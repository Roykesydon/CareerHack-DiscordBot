import time

import discord
import requests
from core.config import CONFIG, LANG_DATA
from core.database import mongo_database
from core.validator import Validator
from discord import app_commands
from discord.ext import commands


class UploadFileCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="upload", description=LANG_DATA["commands"]["upload"]["description"]
    )
    async def upload_document(self, interaction, attachment: discord.Attachment):
        if not Validator.in_dm_or_enabled_channel(interaction.channel):
            await interaction.response.send_message(
                f"{LANG_DATA['permission']['dm-or-enabled-channel-only']}"
            )
            return

        async with interaction.channel.typing():
            """
            TODO: check document type, size
            """
            response = requests.get(attachment.url)

            file_name = attachment.filename
            insert_data = {
                "file_name": file_name,
                "file_type": attachment.content_type,
                "file_url": attachment.url,
                "file_time": int(time.time()),
                "user_id": interaction.user.id,
            }
            mongo_database["UserUploadFile"].insert_one(insert_data)

            # get document id from mongo as file name
            # save file to local storage
            file = mongo_database["UserUploadFile"].find_one(insert_data)
            if file is not None:
                file_name = str(file["_id"])

            with open(f"{CONFIG['storage_path']}/{file_name}", "wb") as file:
                file.write(response.content)

        return await interaction.response.send_message(
            LANG_DATA["commands"]["upload"]["success"]
        )

    def cog_check(self, ctx):
        # check if the command is used in a channel that is enabled or in a DM
        return not isinstance(ctx.channel, discord.DMChannel)


async def setup(bot):
    await bot.add_cog(UploadFileCommand(bot))
