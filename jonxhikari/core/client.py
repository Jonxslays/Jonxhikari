import typing as t
from pathlib import Path

import hikari
import tanjun


class SlashClient(tanjun.Client):
    """Client for handling Slash Commands."""
    def __init__(self, *args: t.Any, **kwargs: t.Any) -> None:
        super().__init__(*args, **kwargs)
        print("SlashClient initialized!")

    def load_modules(self, *modules: t.Union[str, Path]) -> "SlashClient":
        """Loads Tanjun modules."""
        return super().load_modules(
            *(f"jonxhikari.core.modules.{p.stem}" for p in Path(".").glob("./jonxhikari/core/modules/*.py"))
        )

    @classmethod
    def from_gateway_bot(
        cls,
        bot: hikari.traits.GatewayBotAware,
        /,
        *,
        event_managed: bool = True,
        mention_prefix: bool = False,
        set_global_commands: t.Union[hikari.Snowflake, bool] = False,
    ) -> "SlashClient":
        return (
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
