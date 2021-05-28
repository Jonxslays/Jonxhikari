import hikari
import lightbulb
from pathlib import Path

from jonxhikari import Secrets


class Bot(lightbulb.Bot):
    def __init__(self, version):
        self.version = version
        self._plugins = [
            p.stem for p in Path(".").glob("./jonxhikari/bot/plugins/*.py")
        ]

        super().__init__(
            token = Secrets.TOKEN,
            intents=hikari.Intents.ALL,
            prefix=">>",
            insensitive_commands=True,
            ignore_bots=True
        )

    def setup(self):
        for plugin in self._plugins:
            self.load_extension(f"jonxhikari.bot.plugins.{plugin}")
            print(f" - {plugin} loaded")

        print("setup complete")

    def run(self):
        self.setup()
        print("running bot")
        super().run()
