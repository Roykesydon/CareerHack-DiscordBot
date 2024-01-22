from pathlib import Path

import discord
from discord.ext import commands

from core.administrator_manager import AdministratorManager
from core.chat_bot import ChatBot
from core.feedback_manager import FeedbackManager
from core.utils.config import CONFIG
from core.validate.admin_validator import AdminValidator
from core.validate.channel_validator import ChannelValidator
from core.validate.user_validator import UserValidator

chat_bot = ChatBot()

feedback_manager = FeedbackManager()
administrator_manager = AdministratorManager()

channel_validator = ChannelValidator()
admin_validator = AdminValidator(administrator_manager)
user_validator = UserValidator()


# Load commands
async def load_commands(bot):
    for cog in [path.stem for path in Path("./application/commands").glob("*.py")]:
        await bot.load_extension(f"application.commands.{cog}")
        print(f"Loaded Command - {cog}")


# Load events
async def load_events(bot):
    for cog in [path.stem for path in Path("./application/events").glob("*.py")]:
        await bot.load_extension(f"application.events.{cog}")
        print(f"Loaded Event - {cog}")


def run():
    # intents 是要求的權限
    intents = discord.Intents.all()
    bot = commands.Bot(command_prefix="/", intents=intents)
    bot.remove_command("help")  # remove default help command
    token = CONFIG["discord"]["token"]

    @bot.event
    async def on_ready():
        if bot.user is not None:
            print(f"Logged in as {bot.user.name}")
        await load_events(bot)
        await load_commands(bot)

        # sync command tree to discord
        slash = await bot.tree.sync()
        print(f"Slash commands synced: {len(slash)}")

    bot.run(token)


if __name__ == "__main__":
    run()
