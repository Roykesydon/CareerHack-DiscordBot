import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Button, View

from core.chat_bot import LLMType
from core.utils.text_manager import TextManager
from main import channel_validator, chat_bot


class ModelSettingCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_response_message(self, interaction, SWITCH_MODEL_TEXT_DICT):
        model_setting = chat_bot.get_model_setting(str(interaction.channel_id))

        response_message = f"{SWITCH_MODEL_TEXT_DICT['current-model-prefix']}"
        response_message += f"{SWITCH_MODEL_TEXT_DICT[chat_bot.get_llm_type(str(interaction.channel_id))]}"
        response_message += (
            f"\n{SWITCH_MODEL_TEXT_DICT['current-secondary-search-prefix']}"
        )
        # emoji check or not
        response_message += "✅" if model_setting["secondary_search"] else "❌"
        response_message += f"\n{SWITCH_MODEL_TEXT_DICT['button-above-message']}"

        return response_message

    @app_commands.command(
        name="model-setting",
        description=TextManager.DEFAULT_LANG_DATA["commands"]["model-setting"][
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
            view = View()

            SWITCH_MODEL_TEXT_DICT = LANG_DATA["commands"]["model-setting"]

            async def gpt3_callback(interaction):
                chat_bot.switch_model(
                    channel_id=str(interaction.channel_id), llm_type=LLMType.GPT3
                )

                response_message = self.get_response_message(
                    interaction, SWITCH_MODEL_TEXT_DICT
                )

                await interaction.response.edit_message(
                    content=response_message, view=view
                )

            async def gpt4_callback(interaction):
                chat_bot.switch_model(
                    channel_id=str(interaction.channel_id), llm_type=LLMType.GPT4
                )

                response_message = self.get_response_message(
                    interaction, SWITCH_MODEL_TEXT_DICT
                )

                await interaction.response.edit_message(
                    content=response_message, view=view
                )

            async def offline_callback(interaction):
                chat_bot.switch_model(
                    channel_id=str(interaction.channel_id), llm_type=LLMType.OFFLINE
                )

                response_message = self.get_response_message(
                    interaction, SWITCH_MODEL_TEXT_DICT
                )

                await interaction.response.edit_message(
                    content=response_message, view=view
                )

            async def open_secondary_search_callback(interaction):
                chat_bot.set_secondary_search(
                    channel_id=str(interaction.channel_id), secondary_search=True
                )
                response_message = self.get_response_message(
                    interaction, SWITCH_MODEL_TEXT_DICT
                )

                await interaction.response.edit_message(
                    content=response_message, view=view
                )

            async def close_secondary_search_callback(interaction):
                chat_bot.set_secondary_search(
                    channel_id=str(interaction.channel_id), secondary_search=False
                )
                response_message = self.get_response_message(
                    interaction, SWITCH_MODEL_TEXT_DICT
                )

                await interaction.response.edit_message(
                    content=response_message, view=view
                )

            # add buttons
            gpt3_button = Button(
                label=f"{SWITCH_MODEL_TEXT_DICT['gpt3']}",
                style=discord.ButtonStyle.primary,
                row=1,
            )
            gpt3_button.callback = gpt3_callback
            view.add_item(gpt3_button)

            gpt4_button = Button(
                label=f"{SWITCH_MODEL_TEXT_DICT['gpt4']}",
                style=discord.ButtonStyle.primary,
                row=1,
            )
            gpt4_button.callback = gpt4_callback
            view.add_item(gpt4_button)

            offline_button = Button(
                label=f"{SWITCH_MODEL_TEXT_DICT['offline']}",
                style=discord.ButtonStyle.primary,
                row=1,
            )
            offline_button.callback = offline_callback
            view.add_item(offline_button)

            open_secondary_search_button = Button(
                label=f"{SWITCH_MODEL_TEXT_DICT['open-secondary-search']}",
                style=discord.ButtonStyle.primary,
                row=2,
            )
            open_secondary_search_button.callback = open_secondary_search_callback
            view.add_item(open_secondary_search_button)

            close_secondary_search_button = Button(
                label=f"{SWITCH_MODEL_TEXT_DICT['close-secondary-search']}",
                style=discord.ButtonStyle.primary,
                row=2,
            )
            close_secondary_search_button.callback = close_secondary_search_callback
            view.add_item(close_secondary_search_button)

            response_message = self.get_response_message(
                interaction, SWITCH_MODEL_TEXT_DICT
            )

            await interaction.response.send_message(response_message, view=view)


async def setup(bot):
    await bot.add_cog(ModelSettingCommand(bot))
