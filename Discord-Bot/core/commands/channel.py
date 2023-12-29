import asyncio

import discord
from core.config import LANG_DATA
from core.validator import Validator
from discord import app_commands
from discord.ext import commands
from discord.ui import Button, View


class ChannelCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="channel", description=f"{LANG_DATA['commands']['channel']['description']}"
    )
    async def channel_control(self, interaction):
        # check not in DM
        if isinstance(interaction.channel, discord.DMChannel):
            await interaction.response.send_message(
                f"{LANG_DATA['permission']['dm-not-allowed']}"
            )
            return

        async with interaction.channel.typing():
            response_message = ""
            view = View()

            CHANNEL_TEXT_DICT = LANG_DATA["commands"]["channel"]

            async def enable_callback(interaction):
                Validator.enable_channel(interaction.channel.id)
                await interaction.response.send_message(
                    CHANNEL_TEXT_DICT["enable-response"]
                )

            async def disable_callback(interaction):
                Validator.disable_channel(interaction.channel.id)
                await interaction.response.send_message(
                    CHANNEL_TEXT_DICT["disable-response"]
                )

            # show current status
            enabled = interaction.channel.id in Validator.get_enabled_channels()
            prefix = "✅" if enabled else "❌"
            status = f"{CHANNEL_TEXT_DICT['current-status-prefix']} {prefix} {CHANNEL_TEXT_DICT['enabled'] if enabled else CHANNEL_TEXT_DICT['disabled']}"

            response_message += f"{status}\n"

            # add buttons
            enable_button = Button(
                label=f"{CHANNEL_TEXT_DICT['enable']}",
                style=discord.ButtonStyle.green,
            )
            enable_button.callback = enable_callback
            view.add_item(enable_button)

            disable_button = Button(
                label=f"{CHANNEL_TEXT_DICT['disable']}",
                style=discord.ButtonStyle.red,
            )
            disable_button.callback = disable_callback
            view.add_item(disable_button)

            response_message += f"{CHANNEL_TEXT_DICT['button-above-message']}"

            await interaction.response.send_message(response_message, view=view)


async def setup(bot):
    await bot.add_cog(ChannelCommand(bot))
