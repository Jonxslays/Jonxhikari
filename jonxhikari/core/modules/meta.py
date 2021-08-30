import random
from time import time

import hikari
import tanjun

from jonxhikari import SlashClient


component = tanjun.Component()


@component.with_command
@tanjun.as_slash_command("ping", "get a response from the bot")
async def ping_command(ctx: tanjun.abc.Context) -> None:
    start = time()
    await ctx.respond("uwu-owo")
    end = time()

    await ctx.edit_initial_response(
        f"**Gateway**: {ctx.client.bot.heartbeat_latency * 1000:,.0f} ms\n**REST**: {(end - start) * 1000:,.0f} ms",
    )


@tanjun.as_loader
def load_component(client: SlashClient) -> None:
    client.add_component(component.copy())
