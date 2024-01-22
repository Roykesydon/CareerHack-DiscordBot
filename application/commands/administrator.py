import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Button, View

from core.utils.text_manager import TextManager
from main import (admin_validator, administrator_manager, channel_validator,
                  user_validator)


class AdministratorCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="administrator",
        description=TextManager.DEFAULT_LANG_DATA["commands"]["administrator"][
            "description"
        ],
    )
    async def administrator_control(self, interaction):
        text_manager = TextManager()
        LANG_DATA = text_manager.get_selected_language(str(interaction.channel_id))

        # check in DM or not
        if not isinstance(interaction.channel, discord.DMChannel):
            await interaction.response.send_message(
                f"{LANG_DATA['permission']['dm-only']}"
            )
            return

        # check if user is admin
        if not admin_validator.is_admin(str(interaction.user.id)):
            await interaction.response.send_message(
                f"{LANG_DATA['permission']['admin-only']}"
            )
            return

        async with interaction.channel.typing():
            view = View()

            administrator_manager.init_index(str(interaction.channel_id))

            def disable_remove_if_self():
                remove_admin_button.disabled = administrator_manager.get_current_admin(
                    str(interaction.channel_id)
                )[0] == str(interaction.user.id)

            async def leftest_callback(interaction):
                administrator_manager.update_index(str(interaction.channel_id), -999)
                disable_remove_if_self()
                await interaction.message.edit(
                    embed=administrator_manager.get_admin_embed(
                        str(interaction.channel_id)
                    ),
                    view=view,
                )
                await interaction.response.defer()

            async def rightest_callback(interaction):
                administrator_manager.update_index(str(interaction.channel_id), 999)
                disable_remove_if_self()
                await interaction.message.edit(
                    embed=administrator_manager.get_admin_embed(
                        str(interaction.channel_id)
                    ),
                    view=view,
                )
                await interaction.response.defer()

            async def previous_callback(interaction):
                administrator_manager.update_index(str(interaction.channel_id), -1)
                disable_remove_if_self()
                await interaction.message.edit(
                    embed=administrator_manager.get_admin_embed(
                        str(interaction.channel_id)
                    ),
                    view=view,
                )
                await interaction.response.defer()

            async def next_callback(interaction):
                administrator_manager.update_index(str(interaction.channel_id), 1)
                disable_remove_if_self()
                await interaction.message.edit(
                    embed=administrator_manager.get_admin_embed(
                        str(interaction.channel_id)
                    ),
                    view=view,
                )
                await interaction.response.defer()

            leftest_button = Button(
                label=f"|◀",
                style=discord.ButtonStyle.primary,
                row=0,
            )
            previous_button = Button(
                label=f"◀",
                style=discord.ButtonStyle.primary,
                row=0,
            )
            next_button = Button(
                label=f"▶",
                style=discord.ButtonStyle.primary,
                row=0,
            )
            rightest_button = Button(
                label=f"▶|",
                style=discord.ButtonStyle.primary,
                row=0,
            )
            leftest_button.callback = leftest_callback
            previous_button.callback = previous_callback
            next_button.callback = next_callback
            rightest_button.callback = rightest_callback

            view.add_item(leftest_button)
            view.add_item(previous_button)
            view.add_item(next_button)
            view.add_item(rightest_button)

            async def remove_callback(interaction):
                await interaction.message.delete()
                (
                    current_admin_id,
                    current_admin_name,
                ) = administrator_manager.get_current_admin(str(interaction.channel_id))

                # can't remove self
                if current_admin_id == str(interaction.user.id):
                    await interaction.channel.send(
                        f"{LANG_DATA['commands']['administrator']['cannot-remove-self']}"
                    )
                    await interaction.response.defer()
                    return

                administrator_manager.remove_admin(
                    channel_id=str(interaction.channel_id)
                )

                remove_success = LANG_DATA["commands"]["administrator"][
                    "remove-success"
                ]
                remove_prefix = remove_success.split("%")[0]
                remove_suffix = remove_success.split("%")[1]

                await interaction.channel.send(
                    f"{remove_prefix} {current_admin_name} {remove_suffix}"
                )

            async def new_admin_callback(interaction):
                (
                    current_admin_id,
                    current_admin_name,
                ) = administrator_manager.get_current_admin(str(interaction.channel_id))

                await interaction.message.delete()
                # wait for user to send a id
                await interaction.channel.send(
                    f"{LANG_DATA['commands']['administrator']['add-message']}"
                )
                await interaction.response.defer()

                while True:
                    try:
                        user_id = await self.bot.wait_for(
                            "message",
                            timeout=60,
                            check=lambda message: message.author == interaction.user,
                        )
                        user_id = user_id.content
                    except TimeoutError:
                        await interaction.channel.send(
                            f"{LANG_DATA['commands']['administrator']['timeout']}"
                        )
                        return
                    else:
                        if not user_validator.is_user_id_valid(user_id):
                            await interaction.channel.send(
                                f"{LANG_DATA['commands']['administrator']['invalid-user-id']}"
                            )
                        elif admin_validator.is_admin(user_id):
                            await interaction.channel.send(
                                f"{LANG_DATA['commands']['administrator']['already-admin']}"
                            )
                        else:
                            administrator_manager.add_admin(str(user_id))

                            add_success = LANG_DATA["commands"]["administrator"][
                                "add-success"
                            ]
                            add_prefix = add_success.split("%")[0]
                            add_suffix = add_success.split("%")[1]

                            await interaction.channel.send(
                                f"{add_prefix} {current_admin_name} {add_suffix}"
                            )
                        return

            remove_admin_button = Button(
                label=f"{LANG_DATA['commands']['administrator']['remove-admin-button']}",
                style=discord.ButtonStyle.red,
                row=1,
            )
            new_admin_button = Button(
                label=f"{LANG_DATA['commands']['administrator']['add-admin-button']}",
                style=discord.ButtonStyle.primary,
                row=1,
            )

            remove_admin_button.callback = remove_callback
            new_admin_button.callback = new_admin_callback

            if administrator_manager.get_current_admin(str(interaction.channel_id))[
                0
            ] == str(interaction.user.id):
                remove_admin_button.disabled = True

            view.add_item(remove_admin_button)
            view.add_item(new_admin_button)

            await interaction.response.send_message(
                embed=administrator_manager.get_admin_embed(
                    str(interaction.channel_id)
                ),
                view=view,
            )


async def setup(bot):
    await bot.add_cog(AdministratorCommand(bot))
