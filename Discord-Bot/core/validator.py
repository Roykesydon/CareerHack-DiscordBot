import discord

"""
Bot response permission Control
"""


class Validator:
    _enabled_channels = set()

    @staticmethod
    def in_dm_or_enabled_channel(channel):
        # check if the command is used in a channel that is enabled or in a DM
        return channel.id in Validator._enabled_channels or isinstance(
            channel, discord.DMChannel
        )

    @staticmethod
    def enable_channel(channel_id):
        if channel_id not in Validator._enabled_channels:
            Validator._enabled_channels.add(channel_id)

    @staticmethod
    def disable_channel(channel_id):
        if channel_id in Validator._enabled_channels:
            Validator._enabled_channels.discard(channel_id)

    """
    getters
    """

    @staticmethod
    def get_enabled_channels():
        return Validator._enabled_channels
