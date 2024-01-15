import discord
from bson.objectid import ObjectId
from discord.ext import commands
from discord.ui import Button, View

from core.config import CONFIG
from core.database import mongo_database
from core.text_manager import TextManager
from core.validator import Validator
from main import hacker_rank_tools


class DirectlyChat(commands.Cog):
    START_CHAT_CHANNEL_SET = set()
    CHANNEL_FILE_SCOPE_DICT = {}

    @staticmethod
    def insert_start_chat_channel(channel_id: str):
        DirectlyChat.START_CHAT_CHANNEL_SET.add(channel_id)

    @staticmethod
    def remove_start_chat_channel(channel_id: str):
        DirectlyChat.START_CHAT_CHANNEL_SET.remove(channel_id)

    @staticmethod
    def set_channel_file_scope(channel_id: str, file_id_list: list):
        filename_list = []
        db_collection = mongo_database.get_collection("UserUploadFile")

        for file_id in file_id_list:
            # search for filename_extension
            extension = db_collection.find_one({"_id": ObjectId(file_id)})
            if extension is not None:
                extension = extension["filename_extension"]
            filename_list.append(f"{file_id}.{extension}")

        DirectlyChat.CHANNEL_FILE_SCOPE_DICT[channel_id] = filename_list

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        text_manager = TextManager()
        LANG_DATA = text_manager.get_selected_language(str(message.channel.id))

        # Ignore message from bot
        if message.author == self.bot.user:
            return

        # if user want to stop chat
        if message.content == "/end":
            if str(message.channel.id) in DirectlyChat.START_CHAT_CHANNEL_SET:
                async with message.channel.typing():
                    self.remove_start_chat_channel(str(message.channel.id))
                    await message.channel.send(LANG_DATA["commands"]["ask"]["end"])
            return

        # Ignore message that start with /
        if message.content.startswith("/"):
            return

        # check if the command is used in a channel that is enabled or in a DM
        if not Validator.in_dm_or_enabled_channel(message.channel):
            return

        # check if this channel start chat
        if str(message.channel.id) not in DirectlyChat.START_CHAT_CHANNEL_SET:
            return

        async with message.channel.typing():
            query = message.content

            ans, contents, metadatas = hacker_rank_tools.chat(
                query, DirectlyChat.CHANNEL_FILE_SCOPE_DICT[str(message.channel.id)]
            )

            view = View()
            # check refernece button
            reference_button = Button(
                label=LANG_DATA["events"]["directly_chat"]["reference_button_text"],
                style=discord.ButtonStyle.primary,
            )

            async def show_reference(interaction):
                color = CONFIG["primary_color"]
                color_int = int(color.replace("#", ""), 16)
                embed = discord.Embed(
                    title=LANG_DATA["events"]["directly_chat"]["reference_embed_title"],
                    color=color_int,
                )

                collection = mongo_database.get_collection("UserUploadFile")

                if metadatas is not None:
                    for index, metadata in enumerate(metadatas):
                        # get custom_file_name
                        custom_file_name = collection.find_one(
                            {"_id": ObjectId(metadata["source"].split(".")[0])}
                        )

                        if custom_file_name is not None:
                            custom_file_name = custom_file_name["custom_file_name"]
                        # with divider
                        if index != 0:
                            embed.add_field(
                                name="\n",
                                value="",
                                inline=True,
                            )
                        if contents is not None:
                            source_content = f"{LANG_DATA['events']['directly_chat']['content_prefix']}\
                                {contents[index]}\n{LANG_DATA['events']['directly_chat']['source_prefix']}\
                                    {custom_file_name}\n{LANG_DATA['events']['directly_chat']['page_prefix']}\
                                        {metadata['page']+1}"

                            embed.add_field(
                                name=f"{LANG_DATA['events']['directly_chat']['field_name']} {index+1}",
                                value=source_content,
                                inline=False,
                            )

                    # disable button
                    reference_button.disabled = True

                    await interaction.response.edit_message(view=view)
                    await interaction.followup.send(embed=embed)

            reference_button.callback = show_reference
            view.add_item(reference_button)

        return await message.channel.send(ans, view=view)


async def setup(bot):
    await bot.add_cog(DirectlyChat(bot))
