from pathlib import Path

import discord
from core.config import CONFIG
from discord.ext import commands


# Load commands
async def load_commands(bot):
    for cog in [path.stem for path in Path("./core/commands").glob("*.py")]:
        await bot.load_extension(f"core.commands.{cog}")
        print(f"Loaded Command - {cog}")


# Load events
async def load_events(bot):
    for cog in [path.stem for path in Path("./core/events").glob("*.py")]:
        await bot.load_extension(f"core.events.{cog}")
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