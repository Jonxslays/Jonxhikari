import hikari
import lightbulb
import time

import jonxhikari


class Misc(lightbulb.Plugin):
    """Items not fitting in elsewhere."""
    def __init__(self, bot: jonxhikari.Bot) -> None:
        self.bot = bot
        super().__init__()


def load(bot: jonxhikari.Bot) -> None:
    bot.add_plugin(Misc(bot))


def unload(bot: jonxhikari.Bot) -> None:
    bot.remove_plugin("Misc")
