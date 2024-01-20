import asyncio

import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Button, View

from core.utils.text_manager import TextManager
from main import channel_validator, chat_bot


class SwitchModelCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="switch-model",
        description=TextManager.DEFAULT_LANG_DATA["commands"]["switch-model"][
            "description"
        ],
    )
    async def switch_model(self, interaction):
        text_manager = TextManager()
        LANG_DATA = text_manager.get_selected_language(str(interaction.channel_id))

        if not channel_validator.in_dm_or_enabled_channel(interaction.channel):
            await interaction.response.send_message(
                f"{LANG_DATA['permission']['dm-or-enabled-channel-only']}"
            )
            return

        async with interaction.channel.typing():
            response_message = ""
            view = View()

            SWITCH_MODEL_TEXT_DICT = LANG_DATA["commands"]["switch-model"]

            async def online_callback(interaction):
                chat_bot.switch_model(
                    channel_id=str(interaction.channel_id), online=False
                )
                await interaction.message.delete()
                await interaction.channel.send(
                    SWITCH_MODEL_TEXT_DICT["online-response"]
                )

            async def offline_callback(interaction):
                chat_bot.switch_model(
                    channel_id=str(interaction.channel_id), online=False
                )
                await interaction.message.delete()
                await interaction.channel.send(
                    SWITCH_MODEL_TEXT_DICT["offline-response"]
                )

            # show current status
            if chat_bot.is_online(str(interaction.channel_id)):
                status = f"{SWITCH_MODEL_TEXT_DICT['current-model-prefix']}{SWITCH_MODEL_TEXT_DICT['online-model']}"
            else:
                status = f"{SWITCH_MODEL_TEXT_DICT['current-model-prefix']}{SWITCH_MODEL_TEXT_DICT['offline-model']}"

            response_message += f"{status}\n"

            # add buttons
            online_button = Button(
                label=f"{SWITCH_MODEL_TEXT_DICT['online-button']}",
                style=discord.ButtonStyle.primary,
            )
            online_button.callback = online_callback
            view.add_item(online_button)

            offline_button = Button(
                label=f"{SWITCH_MODEL_TEXT_DICT['offline-button']}",
                style=discord.ButtonStyle.primary,
            )
            offline_button.callback = offline_callback
            view.add_item(offline_button)

            response_message += f"{SWITCH_MODEL_TEXT_DICT['button-above-message']}"

            await interaction.response.send_message(response_message, view=view)


async def setup(bot):
    await bot.add_cog(SwitchModelCommand(bot))
