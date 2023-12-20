import discord
from discord.ext import commands

class DirectlyChat(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # Ignore message from bot
        if message.author == self.bot.user:
            return

        # Ignore message that start with /
        if message.content.startswith("/"):
            return

        async with message.channel.typing():
            """
            TODO: get response from chatbot
            """
            chatbot_message = "測試用 LLM 回覆訊息"

        return await message.channel.send(chatbot_message)


async def setup(bot):
    await bot.add_cog(DirectlyChat(bot))
