import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

import lightbulb
import hikari
import uvloop
from aiohttp import ClientSession
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from jonxhikari import Secrets
from jonxhikari.db import Database


class Bot(lightbulb.Bot):
    def __init__(self, version: str) -> None:
        self._plugins = [p.stem for p in Path(".").glob("./jonxhikari/bot/plugins/*.py")]
        self._dynamic = "./jonxhikari/data/dynamic"
        self._static = "./jonxhikari/data/static"
        self.version = version
        self.guilds = {}

        self.scheduler = AsyncIOScheduler()
        self.session = ClientSession()
        self.db = Database(self)
        self.logging_config()
        uvloop.install()

        super().__init__(
            token = Secrets.TOKEN,
            intents = hikari.Intents.ALL,
            prefix = ">>",
            insensitive_commands = True,
            ignore_bots = True,
        )

        # Events we care about
        subscriptions = {
            hikari.StartingEvent: self.on_starting,
            hikari.StartedEvent: self.on_started,
            hikari.StoppingEvent: self.on_stopping,
            hikari.GuildAvailableEvent: self.on_guild_available,
        }

        # Subscribe to events
        for key in subscriptions:
            self.event_manager.subscribe(key, subscriptions[key])

    # Logs to a file that rotates weekly
    def logging_config(self) -> None:
        self.log = logging.getLogger("root")
        self.log.setLevel(logging.INFO)

        trfh = TimedRotatingFileHandler(
            "./jonxhikari/data/logs/main.log",
            when="D", interval=7, encoding="utf-8",
            backupCount=14
        )

        ff = logging.Formatter(
            "[%(asctime)s] %(levelname)s ||| %(message)s"
        )

        trfh.setFormatter(ff)
        self.log.addHandler(trfh)

    # Fires on new guild join, on startup, and after disconnect
    async def on_guild_available(self, event: hikari.GuildAvailableEvent) -> None:
        if event.guild.id not in self.guilds:
            await self.db.execute(
                "INSERT OR IGNORE INTO guilds (GuildID) VALUES (?)",
                event.guild_id
            )

    # Fires before bot is connected
    # Blocks full connection until complete
    async def on_starting(self, event: hikari.StartingEvent) -> None:
        await self.db.connect()

        # List of tuples containing guild ID and prefix
        for guild in await self.db.records("SELECT * FROM guilds"):

            # Cache prefixes into self.guilds
            self.guilds[guild[0]] = {
                "prefix": guild[1]
            }

        # Load plugins from extensions
        for plugin in self._plugins:
            self.load_extension(f"jonxhikari.bot.plugins.{plugin}")

    # Fires once bot is fully connected
    async def on_started(self, _: hikari.StartedEvent) -> None:
        self.scheduler.start()
        await self.db.sync()

    # Fires at the beginning of shutdown sequence
    async def on_stopping(self, _: hikari.StoppingEvent) -> None:
        self.scheduler.shutdown()
        await self.session.close()
        await self.db.close()
