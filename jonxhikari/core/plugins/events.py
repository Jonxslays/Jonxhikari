import datetime

from hikari.messages import Attachment
import lightbulb
import hikari
import tanjun


class Events(lightbulb.Plugin):
    """Jonxhikaris pseudo event handler."""
    def __init__(self, bot: lightbulb.Bot) -> None:
        self.bot = bot
        super().__init__()

    @lightbulb.plugins.listener()
    async def on_cmd(self, _: lightbulb.CommandCompletionEvent) -> None:
        """Fires on completion of a command."""
        self.bot._invokes += 1

    @lightbulb.plugins.listener()
    async def on_interaction(self, event: hikari.InteractionCreateEvent) -> None:
        """Fires on creations of an interaction."""
        self.bot._invokes += 1
        # TODO research interaction events on a lower level to
        # prevent this from firing multiple times per command

    @lightbulb.plugins.listener()
    async def on_cmd_exc(self, event: lightbulb.CommandErrorEvent) -> None:
        """Handles Lightbulb command exception events."""
        await self.bot.errors.parse_lightbulb(event.exception, event.context)

    @lightbulb.plugins.listener()
    async def on_exc(self, event: hikari.ExceptionEvent) -> None: # type: ignore
        """Handles other exception events."""
        await self.bot.errors.parse(event.exception)


def load(bot: lightbulb.Bot) -> None:
    bot.add_plugin(Events(bot))


def unload(bot: lightbulb.Bot) -> None:
    bot.remove_plugin("Events")
