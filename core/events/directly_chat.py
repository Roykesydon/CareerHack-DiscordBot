import discord
from core.validator import Validator
from discord.ext import commands


class DirectlyChat(commands.Cog):
    START_CHAT_CHANNEL_SET = set()

    @staticmethod
    def insert_start_chat_channel(channel_id: str):
        DirectlyChat.START_CHAT_CHANNEL_SET.add(channel_id)

    @staticmethod
    def remove_start_chat_channel(channel_id: str):
        DirectlyChat.START_CHAT_CHANNEL_SET.remove(channel_id)

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # Ignore message from bot
        if message.author == self.bot.user:
            return

        # if user want to stop chat
        if message.content == "/end":
            self.remove_start_chat_channel(str(message.channel.id))
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
            """
            TODO: get response from chatbot
            """
            chatbot_message = "測試用 LLM 回覆訊息"

        return await message.channel.send(chatbot_message)


async def setup(bot):
    await bot.add_cog(DirectlyChat(bot))
