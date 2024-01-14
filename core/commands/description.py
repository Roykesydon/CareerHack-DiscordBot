import discord
from discord import app_commands
from discord.ext import commands

from core.message import Message
from core.text_manager import TextManager
from core.validator import Validator


class DescriptionCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="description",
        description=TextManager.DEFAULT_LANG_DATA["commands"]["description"][
            "description"
        ],
    )
    async def show_description(self, interaction):
        text_manager = TextManager()
        LANG_DATA = text_manager.get_selected_language(str(interaction.channel_id))

        if not Validator.in_dm_or_enabled_channel(interaction.channel):
            await interaction.response.send_message(
                f"{LANG_DATA['permission']['dm-or-enabled-channel-only']}"
            )
            return

        async with interaction.channel.typing():
            logo = discord.File("./assets/logo.png")
            description = LANG_DATA["description"]["content"]

            # set embed fields
            embed_fields = {}
            for field_name, field_info in LANG_DATA["description"]["embed"][
                "fields"
            ].items():
                embed_fields[field_info["name"]] = field_info["value"]

            for command in self.bot.tree.walk_commands():
                field_title = LANG_DATA["commands"][command.name]["field-name"]
                if field_title == LANG_DATA["commands"]["help"]["field-name"]:
                    icon = LANG_DATA["commands"][command.name]["icon"]
                    command_description = LANG_DATA["commands"][command.name][
                        "description"
                    ]
                    if field_title in embed_fields:
                        embed_fields[
                            field_title
                        ] += f"{icon} `/{command.name}` - {command_description}\n"
                    else:
                        embed_fields[
                            field_title
                        ] = f"{icon} `/{command.name}` - {command_description}\n"

            message = Message(text=description, field=embed_fields, img=logo)

            embed = message.get_embed_format(
                title=LANG_DATA["description"]["embed"]["title"]
            )

            return await interaction.response.send_message(embed=embed, file=logo)


async def setup(bot):
    await bot.add_cog(DescriptionCommand(bot))
