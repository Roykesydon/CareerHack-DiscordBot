import discord
from bson.objectid import ObjectId
from discord.ext import commands
from discord.ui import Button, View

from core.commands.switch_model import SwitchModelCommand
from core.utils.config import CONFIG
from core.utils.database import mongo_database
from core.utils.text_manager import TextManager
from main import channel_validator, chat_bot


class DirectlyChat(commands.Cog):
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
            if str(message.channel.id) in chat_bot.get_start_chat_channel_set():
                async with message.channel.typing():
                    chat_bot.remove_start_chat_channel(str(message.channel.id))
                    await message.channel.send(LANG_DATA["commands"]["ask"]["end"])
            return

        # Ignore message that start with /
        if message.content.startswith("/"):
            return

        # check if the command is used in a channel that is enabled or in a DM
        if not channel_validator.in_dm_or_enabled_channel(message.channel):
            return

        # check if this channel start chat
        if str(message.channel.id) not in chat_bot.get_start_chat_channel_set():
            return

        async with message.channel.typing():
            query = message.content

            ans, contents, metadatas = chat_bot.chat(
                query,
                chat_bot.get_channel_file_scope(str(message.channel.id)),
                str(message.channel.id),
            )

            view = View()
            # check refernece button
            reference_button = Button(
                label=LANG_DATA["events"]["directly_chat"]["reference_button_text"],
                style=discord.ButtonStyle.primary,
            )

            reference_button.callback = chat_bot.get_show_reference_callback(
                channel_id=str(message.channel.id),
                contents=contents,
                metadatas=metadatas,
                reference_button=reference_button,
                view=view,
            )
            view.add_item(reference_button)

        return await message.channel.send(ans, view=view)


async def setup(bot):
    await bot.add_cog(DirectlyChat(bot))
