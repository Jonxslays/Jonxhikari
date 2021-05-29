import lightbulb
import hikari


class Events(lightbulb.Plugin):
    def __init__(self, bot: lightbulb.Bot) -> None:
        self.bot = bot
        super().__init__()

    # Fires on completion of a command
    @lightbulb.plugins.listener()
    async def on_cmd(self, event: lightbulb.CommandCompletionEvent) -> None:
        self.bot._invokes += 1

    # Handles Lightbulb command exception events
    @lightbulb.plugins.listener()
    async def on_cmd_exc(self, event: lightbulb.CommandErrorEvent) -> None:
        await self.bot.errors.parse(event.context, event.exception)


def load(bot: lightbulb.Bot) -> None:
    bot.add_plugin(Events(bot))


def unload(bot: lightbulb.Bot) -> None:
    bot.remove_plugin("Events")
