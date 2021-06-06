import lightbulb
import hikari


class Events(lightbulb.Plugin):
    def __init__(self, bot: lightbulb.Bot) -> None:
        self.bot = bot
        super().__init__()

    @lightbulb.plugins.listener()
    async def on_cmd(self, _: lightbulb.CommandCompletionEvent) -> None:
        """Fires on completion of a command"""
        self.bot._invokes += 1

    @lightbulb.plugins.listener()
    async def on_cmd_exc(self, event: lightbulb.CommandErrorEvent) -> None:
        """Handles Lightbulb command exception events."""
        await self.bot.errors.parse(event.context, event.exception)


def load(bot: lightbulb.Bot) -> None:
    bot.add_plugin(Events(bot))


def unload(bot: lightbulb.Bot) -> None:
    bot.remove_plugin("Events")
