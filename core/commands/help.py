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
                        "emb-title": LANG_DATA["commands"][command.name]["emb-title"],
                        "name": command.name,
                        "icon": LANG_DATA["commands"][command.name]["icon"],
                        "description": LANG_DATA["commands"][command.name][
                            "description"
                        ],
                    }
                )

            # set commands list description
            # description = ""
            # for command in commands_list_with_description:
            #     description += f"{command['icon']} `/{command['name']}` - {command['description']}\n"

            # message = Message(text=description)

            # define custom order
            custom_order = [
                LANG_DATA["commands"]["help"]["emb-title"],
                LANG_DATA["commands"]["ask"]["emb-title"],
                LANG_DATA["commands"]["upload"]["emb-title"],
                LANG_DATA["commands"]["channel"]["emb-title"],
            ]

            # sort commands using custom order
            commands_list_with_description.sort(
                key=lambda x: custom_order.index(x["emb-title"])
            )

            embed_text = {}
            for command in commands_list_with_description:
                emb_title = command["emb-title"]
                if emb_title in embed_text:
                    embed_text[
                        emb_title
                    ] += f"{command['icon']} `/{command['name']}` - {command['description']}\n"
                else:
                    embed_text[
                        emb_title
                    ] = f"{command['icon']} `/{command['name']}` - {command['description']}\n"

            message = Message(text=embed_text)

            embed = message.get_embed_format(
                title=LANG_DATA["commands"]["help"]["title"]
            )

            await interaction.response.send_message(embed=embed)

    def cog_check(self, ctx):
        return Validator.in_dm_or_enabled_channel(ctx)


async def setup(bot):
    await bot.add_cog(HelpCommand(bot))
