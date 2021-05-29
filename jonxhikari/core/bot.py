import logging
import time
import typing as t
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

import lightbulb
import hikari
import uvloop
from aiohttp import ClientSession
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from jonxhikari import Secrets
from jonxhikari.core.db import Database
from jonxhikari.core.utils import Errors


class Bot(lightbulb.Bot):
    def __init__(self, version: str) -> None:
        self._plugins_dir = "./jonxhikari/core/plugins"
        self._plugins = [p.stem for p in Path(".").glob(f"{self._plugins_dir}/*.py")]
        self._dynamic = "./jonxhikari/data/dynamic"
        self._static = "./jonxhikari/data/static"

        self.version = version
        self._invokes = 0
        self.guilds = {}

        self.scheduler = AsyncIOScheduler()
        self.session = ClientSession()
        self.errors = Errors()
        self.db = Database(self)

        self.logging_config()
        uvloop.install()

        # Initiate hikari BotApp superclass
        super().__init__(
            token = Secrets.TOKEN,
            intents = hikari.Intents.ALL,
            prefix = lightbulb.when_mentioned_or(self.grab_prefix),
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

    def logging_config(self) -> None:
        """Logs to a file that rotates weekly"""
        self.log = logging.getLogger("root")
        self.log.setLevel(logging.INFO)

        trfh = TimedRotatingFileHandler(
            "./jonxhikari/data/logs/main.log",
            when="D", interval=3, encoding="utf-8",
            backupCount=10
        )

        ff = logging.Formatter(
            f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] %(levelname)s ||| %(message)s"
        )

        trfh.setFormatter(ff)
        self.log.addHandler(trfh)

    async def on_guild_available(self, event: hikari.GuildAvailableEvent) -> None:
        """fires on new guild join, on startup, and after disconnect"""
        if event.guild_id not in self.guilds:
            await self.db.execute(
                "INSERT OR IGNORE INTO guilds (GuildID) VALUES (?)",
                event.guild_id
            )

    async def on_starting(self, event: hikari.StartingEvent) -> None:
        """Fires before bot is connected. Blocks on_started until complete."""
        await self.db.connect()

        # List of tuples containing guild ID and prefix
        for guild in await self.db.records("SELECT * FROM guilds"):

            # Cache prefixes into self.guilds
            self.guilds[guild[0]] = {
                "prefix": guild[1]
            }

        # Load plugins from extensions
        for plugin in self._plugins:
            self.load_extension(f"jonxhikari.core.plugins.{plugin}")

    async def on_started(self, _: hikari.StartedEvent) -> None:
        """Fires once bot is fully connected"""
        await self.db.sync()
        self.scheduler.start()
        self.add_check(self._dm_commands)

    async def on_stopping(self, _: hikari.StoppingEvent) -> None:
        """Fires at the beginning of shutdown sequence"""
        self.scheduler.shutdown()
        await self.session.close()
        await self.db.close()

    async def grab_prefix(self, bot: lightbulb.Bot, message: hikari.Message) -> str:
        """Grabs a prefix to be used in a particular context"""
        if (_id := message.guild_id) in self.guilds:
            return self.guilds[_id]["prefix"]

        if await self._dm_commands(message):
            return await self.db.field("SELECT Prefix FROM guilds WHERE GuildID = ?", _id)

        return "$"

    #TODO Find a better way. guild_id may not be cached.
    async def _dm_commands(self, message: hikari.Message) -> bool:
        """Prevents commands invocations in DMs"""
        return message.guild_id
