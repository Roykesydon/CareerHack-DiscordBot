import discord
from discord import SelectOption, app_commands, ui
from discord.ext import commands

from core.events.directly_chat import DirectlyChat
from core.text_manager import TextManager
from core.upload_file_manager import UploadFileManager
from core.validator import Validator


class AskScopeSelectView(ui.View):
    def __init__(self, channel_id, user_id):
        super().__init__()

        # Add the dropdown to our view object
        self.add_item(AskScopeSelect(channel_id, user_id))


class AskScopeSelect(ui.Select):
    def __init__(self, channel_id, user_id):
        text_manager = TextManager()
        LANG_DATA = text_manager.get_selected_language(channel_id)

        options = [
            SelectOption(
                label=LANG_DATA["commands"]["ask"]["all_file"],
                value=f"all-{LANG_DATA['commands']['ask']['all_file']}",
            ),
        ]
        upload_file_manager = UploadFileManager()

        for file in upload_file_manager.get_available_file_list(user_id):
            options.append(
                SelectOption(
                    label=file["file_name"],
                    value=f"{file['file_id']}-{file['file_name']}",
                )
            )

        super().__init__(
            placeholder=LANG_DATA["commands"]["ask"]["placeholder"],
            min_values=1,
            max_values=min(15, len(options)),
            options=options,
        )

    async def callback(self, interaction):
        text_manager = TextManager()
        upload_file_manager = UploadFileManager()
        LANG_DATA = text_manager.get_selected_language(str(interaction.channel_id))

        return_message = LANG_DATA["commands"]["ask"]["success"]

        selected_file_scope = self.values
        selected_file_scope = [x.split("-") for x in selected_file_scope]

        # check if "all" is selected with lambda
        if any(list(map(lambda x: x[0] == "all", selected_file_scope))):
            selected_file_id_list = upload_file_manager.get_available_file_list(
                str(interaction.user.id)
            )
            selected_file_id_list = list(
                map(lambda x: x["file_id"], selected_file_id_list)
            )
            selected_file_name_list = [LANG_DATA["commands"]["ask"]["all_file"]]

            return_message += LANG_DATA["commands"]["ask"]["all_file"]
        else:
            selected_file_id_list = list(map(lambda x: x[0], selected_file_scope))
            selected_file_name_list = list(map(lambda x: x[1], selected_file_scope))

        for file_name in selected_file_name_list:
            return_message += f"\n- {file_name}"

        return_message += "\n" + LANG_DATA["commands"]["ask"]["success2"]

        DirectlyChat.insert_start_chat_channel(str(interaction.channel_id))
        DirectlyChat.set_channel_file_scope(
            str(interaction.channel_id), selected_file_id_list
        )

        if interaction.message is not None:
            await interaction.message.delete()

        if isinstance(interaction.channel, discord.channel.TextChannel) or isinstance(
            interaction.channel, discord.channel.DMChannel
        ):
            await interaction.channel.send(return_message)


class AskCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="ask",
        description=TextManager.DEFAULT_LANG_DATA["commands"]["ask"]["description"],
    )
    async def ask_questions(self, interaction):
        text_manager = TextManager()
        LANG_DATA = text_manager.get_selected_language(str(interaction.channel_id))

        if not Validator.in_dm_or_enabled_channel(interaction.channel):
            await interaction.response.send_message(
                f"{LANG_DATA['permission']['dm-or-enabled-channel-only']}"
            )
            return

        async with interaction.channel.typing():
            view = AskScopeSelectView(
                str(interaction.channel_id), str(interaction.user.id)
            )

            return_message = LANG_DATA["commands"]["ask"]["message"]

            await interaction.response.send_message(
                LANG_DATA["commands"]["ask"]["message"], view=view
            )


async def setup(bot):
    await bot.add_cog(AskCommand(bot))
