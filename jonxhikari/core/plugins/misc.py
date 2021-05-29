import lightbulb
import hikari
import time


class Misc(lightbulb.Plugin):
    def __init__(self, bot: lightbulb.Bot) -> None:
        self.bot = bot
        super().__init__()


def load(bot: lightbulb.Bot) -> None:
    bot.add_plugin(Misc(bot))


def unload(bot: lightbulb.Bot) -> None:
    bot.remove_plugin("Misc")
