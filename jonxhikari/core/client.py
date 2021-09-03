import typing as t
from pathlib import Path

import asyncpg
import hikari
import tanjun

from jonxhikari import core


class SlashClient(tanjun.Client):
    """Client for handling Slash Commands."""
    def __init__(self, *args: t.Any, **kwargs: t.Any) -> None:
        self.errors = core.Errors()
        self.embeds = core.Embeds()
        self.bot: core.Bot = kwargs["shard"]

        super().__init__(*args, **kwargs)
        print("SlashClient initialized!")

    def load_modules(self, *modules: t.Union[str, Path]) -> "SlashClient":
        """Loads Tanjun modules."""
        super().load_modules(
            *(f"jonxhikari.core.modules.{p.stem}" for p in Path(".").glob("./jonxhikari/core/modules/*.py"))
        )

        return self

    #
    # TODO might come back to this.
    # Its still not really sorted.
    # Types are wonky and asserts
    # all over the place blegh.
    # >:(
    #
    @classmethod
    def from_gateway_bot(
        cls,
        bot: hikari.GatewayBotAware,
        /,
        *,
        event_managed: bool = True,
        mention_prefix: bool = False,
        set_global_commands: t.Union[hikari.Snowflake, bool] = False,
    ) -> "SlashClient":
        constructor: SlashClient = (
            cls(
                rest=bot.rest,
                cache=bot.cache,
                events=bot.event_manager,
                shard=bot,
                event_managed=event_managed,
                mention_prefix=mention_prefix,
                set_global_commands=set_global_commands,
            )
            .set_human_only()
            .set_hikari_trait_injectors(bot)
        )

        return constructor
