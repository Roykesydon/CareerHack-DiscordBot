import discord
from discord import SelectOption, app_commands, ui
from discord.ext import commands

from core.file_management.upload_file_manager import UploadFileManager
from core.utils.text_manager import TextManager
from main import admin_validator, channel_validator


class TransformFileScopeSelectView(ui.View):
    def __init__(self, channel_id, user_id):
        super().__init__()

        # Add the dropdown to our view object
        self.add_item(TransformFileScopeSelect(channel_id, user_id))


class TransformFileScopeSelect(ui.Select):
    def __init__(self, channel_id, user_id):
        text_manager = TextManager()
        LANG_DATA = text_manager.get_selected_language(channel_id)

        options = []
        upload_file_manager = UploadFileManager()

        for file in upload_file_manager.get_available_file_list(user_id):
            options.append(
                SelectOption(
                    label=file["file_name"], emoji=file["emoji"], value=file["file_id"]
                )
            )

        super().__init__(
            placeholder=LANG_DATA["commands"]["transform-file-scope"]["placeholder"],
            min_values=1,
            max_values=min(15, len(options)),
            options=options,
        )

    async def callback(self, interaction):
        selected_file = self.values
        text_manager = TextManager()
        upload_file_manager = UploadFileManager()

        LANG_DATA = text_manager.get_selected_language(str(interaction.channel_id))

        available_file_list = upload_file_manager.get_available_file_list(
            str(interaction.user.id)
        )

        upload_file_manager.toggle_file_scope(selected_file)

        if interaction.message is not None:
            await interaction.message.delete()

        if isinstance(interaction.channel, discord.channel.TextChannel) or isinstance(
            interaction.channel, discord.channel.DMChannel
        ):
            await interaction.channel.send(
                LANG_DATA["commands"]["transform-file-scope"]["success"]
            )


class TransformFileScopeCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="transform-file-scope",
        description=TextManager.DEFAULT_LANG_DATA["commands"]["transform-file-scope"][
            "description"
        ],
    )
    async def transformFileScope(self, interaction):
        text_manager = TextManager()
        LANG_DATA = text_manager.get_selected_language(str(interaction.channel_id))

        upload_file_manager = UploadFileManager()

        # check in DM or not
        if not channel_validator.in_dm(interaction.channel):
            await interaction.response.send_message(
                f"{LANG_DATA['permission']['dm-only']}"
            )
            return

        if not admin_validator.is_admin(str(interaction.user.id)):
            await interaction.response.send_message(
                f"{LANG_DATA['permission']['admin-only']}"
            )
            return

        private_only = not admin_validator.is_admin(str(interaction.user.id))
        if (
            len(
                upload_file_manager.get_available_file_list(
                    str(interaction.user.id), private_only=private_only
                )
            )
            == 0
        ):
            await interaction.response.send_message(
                f"{LANG_DATA['commands']['download']['no-file']}"
            )
            return

        async with interaction.channel.typing():
            view = TransformFileScopeSelectView(
                str(interaction.channel_id), str(interaction.user.id)
            )
            await interaction.response.send_message(
                LANG_DATA["commands"]["transform-file-scope"]["message"], view=view
            )


async def setup(bot):
    await bot.add_cog(TransformFileScopeCommand(bot))
