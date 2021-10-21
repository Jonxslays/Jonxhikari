import typing as t
from pathlib import Path

import hikari
import tanjun

from jonxhikari import core


class SlashClient(tanjun.Client):
    """Client for handling Slash Commands."""
    def __init__(self, *args: t.Any, **kwargs: t.Any) -> None:
        super().__init__(*args, **kwargs)
        print("SlashClient initialized!")

    def load_modules(self) -> "SlashClient":
        """Loads Tanjun modules."""
        path = "./jonxhikari/core/modules/*.py"
        super().load_modules(*Path(".").glob(path))
        return self

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
                shards=bot,
                event_managed=event_managed,
                mention_prefix=mention_prefix,
                set_global_commands=set_global_commands,
            )
            .set_human_only()
            .set_hikari_trait_injectors(bot)
        )

        return constructor
