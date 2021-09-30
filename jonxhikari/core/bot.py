import typing as t
from pathlib import Path

import aiohttp
import lightbulb
import hikari
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from jonxhikari import Config
from jonxhikari.core import AsyncPGDatabase
from jonxhikari.core import Embeds
from jonxhikari.core import Errors
from jonxhikari.core import SlashClient


class Bot(lightbulb.Bot):
    def __init__(self, version: str) -> None:
        self._plugins_dir = "./jonxhikari/core/plugins"
        self._plugins = [p.stem for p in Path(".").glob(f"{self._plugins_dir}/*.py")]

        self.version = version
        self.invokes = 0
        self.invokes = 0
        self.guilds: dict[int, dict[str, str]] = {}

        self.scheduler = AsyncIOScheduler()
        self.log = Config.logging()
        self.errors = Errors()
        self.embeds = Embeds()
        self.pool = AsyncPGDatabase()

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
            self.subscribe(key, subscriptions[key])

        # Create a Slash Command Client from the Bot
        self.client: SlashClient = SlashClient.from_gateway_bot(
            self, set_global_commands=Config.env("HOME_GUILD", int),
        ).load_modules()

    @property
    def yes(self) -> hikari.KnownCustomEmoji:
        YES = 853792470651502603

        cached_yes = self.cache.get_emoji(YES)
        if isinstance(cached_yes, hikari.KnownCustomEmoji):
            return cached_yes

        fetched_yes = self.rest.fetch_emoji(Config.env("HOME_GUILD", int), YES)
        if isinstance(fetched_yes, hikari.KnownCustomEmoji):
            return fetched_yes

        # We should never get here, but if so
        raise self.errors.wtf("YES emoji is gone! PANIC!")

    @property
    def no(self) -> hikari.KnownCustomEmoji:
        NO = 853792496118267954

        cached_no = self.cache.get_emoji(NO)
        if isinstance(cached_no, hikari.KnownCustomEmoji):
            return cached_no

        fetched_no = self.rest.fetch_emoji(Config.env("HOME_GUILD", int), NO)
        if isinstance(fetched_no, hikari.KnownCustomEmoji):
            return fetched_no

        # We should never get here, but if so
        raise self.errors.wtf("NO emoji is gone! PANIC!")

    async def on_guild_available(self, event: hikari.GuildAvailableEvent) -> None:
        """fires on new guild join, on startup, and after disconnect"""
        if event.guild_id not in self.guilds:
            await self.pool.execute(
                "INSERT INTO guilds (GuildID) VALUES ($1) ON CONFLICT DO NOTHING;",
                event.guild_id
            )

    async def on_starting(self, _: hikari.StartingEvent) -> None:
        """Fires before bot is connected. Blocks on_started until complete."""
        await self.pool.connect()
        self.session = aiohttp.ClientSession()

        # Load plugins from Lightbulb
        for plugin in self._plugins:
            self.load_extension(f"jonxhikari.core.plugins.{plugin}")

    async def on_started(self, _: hikari.StartedEvent) -> None:
        """Fires once bot is fully connected"""

        # List of tuples containing guild ID and prefix or None
        guild_prefix = await self.pool.rows("SELECT GuildID, Prefix FROM guilds;")

        if guild_prefix is not None:
            for guild, prefix in guild_prefix:
                # Cache prefixes into self.guilds
                self.guilds[guild] = {
                    "prefix": prefix
                }

        self.scheduler.start()
        self.add_check(self._dm_command)
        # self.music = self.get_plugin("Music")
        # await self.music.connect()
        # Music is still a work a progress

    async def on_stopping(self, _: hikari.StoppingEvent) -> None:
        """Fires at the beginning of shutdown sequence"""
        await self.pool.close()
        await self.session.close()
        # await self.music.close()
        self.scheduler.shutdown()

    async def resolve_prefix(self, _: lightbulb.Bot, message: hikari.Message) -> str:
        """Grabs a prefix to be used in a particular context"""
        if (id_ := message.guild_id) in self.guilds:
            cached_p: str = self.guilds[id_]["prefix"]
            return cached_p

        elif not await self._dm_command(message):
            fetched_p: str = await self.pool.fetch("SELECT Prefix FROM guilds WHERE GuildID = $1;", id_)
            return fetched_p

        else:
            return "$"

    #TODO Find a better way. guild_id may not be cached.
    async def _dm_command(self, message: hikari.Message) -> bool:
        """Checks if command was invoked in DMs"""
        return message.guild_id is not None
