import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Button, View

from core.file_management.upload_file_manager import UploadFileManager
from core.utils.text_manager import TextManager
from main import channel_validator, chat_bot, feedback_manager


class AskQuickCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="ask-quick",
        description=TextManager.DEFAULT_LANG_DATA["commands"]["ask-quick"][
            "description"
        ],
    )
    async def ask_quick(self, interaction, query: str):
        text_manager = TextManager()
        LANG_DATA = text_manager.get_selected_language(str(interaction.channel_id))

        if not channel_validator.in_dm_or_enabled_channel(interaction.channel):
            await interaction.response.send_message(
                f"{LANG_DATA['permission']['dm-or-enabled-channel-only']}"
            )
            return

        upload_file_manager = UploadFileManager()

        async with interaction.channel.typing():
            await interaction.response.defer()

            selected_file_id_list = upload_file_manager.get_available_file_list(
                str(interaction.user.id)
            )

            if (
                len(
                    upload_file_manager.get_available_file_list(
                        str(interaction.user.id)
                    )
                )
                == 0
            ):
                await interaction.followup.send(
                    f"{LANG_DATA['commands']['ask']['no-file']}"
                )
                return

            selected_file_id_list = list(
                map(lambda x: x["file_id"], selected_file_id_list)
            )
            file_name_list = chat_bot.get_file_name_list(selected_file_id_list)

            processing_message = await interaction.channel.send(
                LANG_DATA["commands"]["ask"]["processing"]
            )

            ans, contents, metadatas = await chat_bot.chat(
                query,
                file_name_list,
                str(interaction.channel.id),
                user_id=str(interaction.user.id),
                processing_message=processing_message,
            )

            print(metadatas)

            view = View()
            # check refernece button
            reference_button = Button(
                label=LANG_DATA["commands"]["ask"]["reference"][
                    "reference_button_text"
                ],
                style=discord.ButtonStyle.primary,
            )

            reference_button.callback = chat_bot.get_show_reference_callback(
                channel_id=str(interaction.channel.id),
                contents=contents,
                metadatas=metadatas,
                reference_button=reference_button,
                view=view,
            )

            if len(metadatas) == 0:
                reference_button.disabled = True

            good_response_button = Button(
                label=LANG_DATA["commands"]["ask"]["feedback"][
                    "good_response_button_text"
                ],
                style=discord.ButtonStyle.success,
            )
            bad_response_button = Button(
                label=LANG_DATA["commands"]["ask"]["feedback"][
                    "bad_response_button_text"
                ],
                style=discord.ButtonStyle.danger,
            )

            good_response_button.callback = feedback_manager.get_good_response_callback(
                channel_id=str(interaction.channel.id),
                good_response_button=good_response_button,
                bad_response_button=bad_response_button,
                view=view,
                query=query,
                answer=ans,
                contents=contents,
                metadatas=metadatas,
            )
            bad_response_button.callback = feedback_manager.get_bad_response_callback(
                channel_id=str(interaction.channel.id),
                good_response_button=good_response_button,
                bad_response_button=bad_response_button,
                view=view,
                query=query,
                answer=ans,
                contents=contents,
                metadatas=metadatas,
            )

            view.add_item(reference_button)
            view.add_item(good_response_button)
            view.add_item(bad_response_button)

        await interaction.followup.send(
            LANG_DATA["commands"]["ask-quick"]["query_prefix"] + query
        )
        await interaction.followup.send(ans, view=view)
        await processing_message.delete()


async def setup(bot):
    await bot.add_cog(AskQuickCommand(bot))
