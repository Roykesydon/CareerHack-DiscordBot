from discord import app_commands
from discord.ext import commands

from core.administrator_manager import AdministratorManager
from core.utils.message import Message
from core.utils.text_manager import TextManager
from main import channel_validator


class HelpCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.administrator_manager = AdministratorManager()
        self.admin_id_list = self.administrator_manager.get_admin_id_list()


    @app_commands.command(
        name="help",
        description=TextManager.DEFAULT_LANG_DATA["commands"]["help"]["description"],
    )
    async def show_command_list(self, interaction):
        text_manager = TextManager()
        LANG_DATA = text_manager.get_selected_language(str(interaction.channel_id))
        user_id = str(interaction.user.id)

        if not channel_validator.in_dm_or_enabled_channel(interaction.channel):
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
                        "field-name": LANG_DATA["commands"][command.name]["field-name"],
                        "name": command.name,
                        "icon": LANG_DATA["commands"][command.name]["icon"],
                        "description": LANG_DATA["commands"][command.name][
                            "description"
                        ],
                    }
                )

            # define custom order
            custom_order = [
                LANG_DATA["commands"]["help"]["field-name"],
                LANG_DATA["commands"]["ask"]["field-name"],
                LANG_DATA["commands"]["upload"]["field-name"],
                LANG_DATA["commands"]["language"]["field-name"],
                LANG_DATA["commands"]["channel"]["field-name"]
            ]                

            # sort commands using custom order
            commands_list_with_description.sort(
                key=lambda x: custom_order.index(x["field-name"])
            )
    
            # set embed fields
            embed_text = {}
            for command in commands_list_with_description:
                field_title = command["field-name"]
                if field_title != LANG_DATA["commands"]["channel"]["field-name"]:
                    if field_title in embed_text:
                        embed_text[
                            field_title
                        ] += f"{command['icon']} `/{command['name']}` - {command['description']}\n"
                    else:
                        embed_text[
                            field_title
                        ] = f"{command['icon']} `/{command['name']}` - {command['description']}\n"
                else:
                    if user_id in self.admin_id_list:
                        if field_title in embed_text:
                            embed_text[
                                field_title
                            ] += f"{command['icon']} `/{command['name']}` - {command['description']}\n"
                        else:
                            embed_text[
                                field_title
                            ] = f"{command['icon']} `/{command['name']}` - {command['description']}\n"

            message = Message(field=embed_text)

            embed = message.get_embed_format(
                title=LANG_DATA["commands"]["help"]["title"]
            )

            await interaction.response.send_message(embed=embed)

    def cog_check(self, ctx):
        return channel_validator.in_dm_or_enabled_channel(ctx)


async def setup(bot):
    await bot.add_cog(HelpCommand(bot))
