import typing as t

import hikari
import tanjun

from jonxhikari import Config, SlashClient


component = tanjun.Component()


async def call_cat_api(client: SlashClient) -> str:
    url = "https://api.thecatapi.com/v1/images/search"
    headers = {"x-api-key": Config.env("CAT_API_KEY")}

    async with client.bot.session.get(url, headers=headers) as response:
        if not 200 <= response.status <= 299:
            return ""

        if not (data := await response.json()):
            return ""

    assert isinstance(d := data[0]["url"], str)
    return d


@component.with_slash_command
@tanjun.as_slash_command("kitties", "Fetch a random kitty")
async def kitties_command(ctx: tanjun.abc.Context) -> None:
    assert isinstance(ctx.client, SlashClient)
    if not (url := await call_cat_api(ctx.client)):
        await ctx.respond(ctx.client.errors.embed(ctx.client, "Unable to fetch a kitty right now :("))
        return None

    e = ctx.client.bot.embeds.build(
        header="Awwww",
        ctx=ctx,
        image=hikari.files.URL(url),
    )

    await ctx.respond(e)


@tanjun.as_loader
def load_component(client: tanjun.abc.Client) -> None:
    client.add_component(component.copy())
