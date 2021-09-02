import typing as t
from pathlib import Path

import aiohttp
import lightbulb
import hikari
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from jonxhikari import Config
from jonxhikari.core import Database
from jonxhikari.core import Embeds
from jonxhikari.core import Errors
from jonxhikari.core import SlashClient


class Bot(lightbulb.Bot):
    def __init__(self, version: str) -> None:
        self._plugins_dir = "./jonxhikari/core/plugins"
        self._plugins = [p.stem for p in Path(".").glob(f"{self._plugins_dir}/*.py")]
        self._dynamic = "./jonxhikari/data/dynamic"
        self._static = "./jonxhikari/data/static"

        self.version = version
        self._invokes = 0
        self.guilds: dict[int, dict[str, t.Union[int, str]]] = {}

        self.scheduler = AsyncIOScheduler()
        self.log = Config.logging()
        self.errors = Errors()
        self.embeds = Embeds()
        self.db = Database(self)

        # Initiate lightbulb Bot superclass
        super().__init__(
            token = Config.env("TOKEN"),
            intents = hikari.Intents.ALL,
            prefix = lightbulb.when_mentioned_or(self.resolve_prefix),
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

        # Create a Slash Command Client from the Bot
        self.client: SlashClient = SlashClient.from_gateway_bot(
            self, set_global_commands=Config.env("HOME_GUILD", int),
        ).load_modules()

        # Attach the Bot to the Client
        assert hasattr(self.client, "bot")
        setattr(self.client, "bot", self)

    @property
    def yes(self) -> hikari.KnownCustomEmoji:
        YES = 853792470651502603

        if cached_yes := self.cache.get_emoji(YES):
            assert isinstance(cached_yes, hikari.KnownCustomEmoji)
            return cached_yes

        if fetched_yes := self.rest.fetch_emoji(Config.env("HOME_GUILD", int), YES):
            assert isinstance(fetched_yes, hikari.KnownCustomEmoji)
            return fetched_yes

        # We should never get here, but if so
        raise self.errors.wtf("YES emoji is gone! PANIC!")

    @property
    def no(self) -> hikari.KnownCustomEmoji:
        NO = 853792496118267954

        if cached_no := self.cache.get_emoji(NO):
            assert isinstance(cached_no, hikari.KnownCustomEmoji)
            return cached_no

        if fetched_no := self.rest.fetch_emoji(Config.env("HOME_GUILD", int), NO):
            assert isinstance(fetched_no, hikari.KnownCustomEmoji)
            return fetched_no

        # We should never get here, but if so
        raise self.errors.wtf("NO emoji is gone! PANIC!")

    async def on_guild_available(self, event: hikari.GuildAvailableEvent) -> None:
        """fires on new guild join, on startup, and after disconnect"""
        if event.guild_id not in self.guilds:
            await self.db.execute(
                "INSERT OR IGNORE INTO guilds (GuildID) VALUES (?)",
                event.guild_id
            )

    async def on_starting(self, _: hikari.StartingEvent) -> None:
        """Fires before bot is connected. Blocks on_started until complete."""
        await self.db.connect()
        self.session = aiohttp.ClientSession()

        # List of tuples containing guild ID and prefix
        for guild in await self.db.records("SELECT GuildID, Prefix FROM guilds"):
            # Cache prefixes into self.guilds
            self.guilds[guild[0]] = {
                "prefix": guild[1]
            }

        # Load plugins from Lightbulb
        for plugin in self._plugins:
            self.load_extension(f"jonxhikari.core.plugins.{plugin}")

    async def on_started(self, _: hikari.StartedEvent) -> None:
        """Fires once bot is fully connected"""
        await self.db.sync()
        self.scheduler.start()
        self.add_check(self._dm_command)

    async def on_stopping(self, _: hikari.StoppingEvent) -> None:
        """Fires at the beginning of shutdown sequence"""
        self.scheduler.shutdown()
        await self.session.close()
        await self.db.close()

    async def resolve_prefix(self, _: lightbulb.Bot, message: hikari.Message) -> str:
        """Grabs a prefix to be used in a particular context"""
        if not message.guild_id:
            return "$"

        if (id_ := message.guild_id) in self.guilds:
            cached_p = self.guilds[id_]["prefix"]
            assert isinstance(cached_p, str)
            return cached_p

        if not await self._dm_command(message):
            fetched_p = await self.db.field("SELECT Prefix FROM guilds WHERE GuildID = ?", id_)
            assert isinstance(fetched_p, str)
            return fetched_p

        return "$"

    #TODO Find a better way. guild_id may not be cached.
    async def _dm_command(self, message: hikari.Message) -> bool:
        """Checks if command was invoked in DMs"""
        return message.guild_id is not None
