import typing as t
from time import time

import tanjun


component = tanjun.Component()


@component.with_slash_command
@tanjun.as_slash_command("ping", "Returns the bot's latency")
async def ping_command(ctx: tanjun.abc.Context) -> None:
    start = time()
    await ctx.respond("uwu-owo")
    end = time()

    assert ctx.client.shards is not None
    await ctx.edit_initial_response(
        f"**Gateway**: {ctx.client.shards.heartbeat_latency * 1000:,.0f} ms\n**REST**: {(end - start) * 1000:,.0f} ms",
    )


@tanjun.as_loader
def load_component(client: tanjun.abc.Client) -> None:
    client.add_component(component.copy())
