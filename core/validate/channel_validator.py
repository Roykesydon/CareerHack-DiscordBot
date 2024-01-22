import discord

"""
Bot response permission Control
"""


class ChannelValidator:
    def __init__(self):
        self._enabled_channels = set()

    def in_dm(self, channel):
        # check if the command is used in a DM
        return isinstance(channel, discord.DMChannel)

    def in_dm_or_enabled_channel(self, channel):
        # check if the command is used in a channel that is enabled or in a DM
        return channel.id in self._enabled_channels or isinstance(
            channel, discord.DMChannel
        )

    def enable_channel(self, channel_id):
        if channel_id not in self._enabled_channels:
            self._enabled_channels.add(channel_id)

    def disable_channel(self, channel_id):
        if channel_id in self._enabled_channels:
            self._enabled_channels.discard(channel_id)

    """
    getters
    """

    def get_enabled_channels(self):
        return self._enabled_channels
