from discord import app_commands
from discord.ext import commands

from core.message import Message
from core.text_manager import TextManager
from core.validator import Validator


class HelpCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="help",
        description=TextManager.DEFAULT_LANG_DATA["commands"]["help"]["description"],
    )
    async def show_command_list(self, interaction):
        text_manager = TextManager()
        LANG_DATA = text_manager.get_selected_language(str(interaction.channel_id))

        if not Validator.in_dm_or_enabled_channel(interaction.channel):
            await interaction.response.send_message(
                f"{LANG_DATA['permission']['dm-or-enabled-channel-only']}"
            )
            return

        async with interaction.channel.typing():
            # list all commands extension
            commands_list_with_description = []
            for command in self.bot.tree.walk_commands():
                commands_list_with_description.append(
                    {
                        "name": command.name,
                        "description": LANG_DATA["commands"][command.name][
                            "description"
                        ],
                    }
                )

            # set commands list description
            description = ""
            for command in commands_list_with_description:
                description += f"**/{command['name']}** - {command['description']}\n"

            message = Message(text=description)

            embed = message.get_embed_format(
                title=LANG_DATA["commands"]["help"]["title"]
            )

            await interaction.response.send_message(embed=embed)

    def cog_check(self, ctx):
        return Validator.in_dm_or_enabled_channel(ctx)


async def setup(bot):
    await bot.add_cog(HelpCommand(bot))
