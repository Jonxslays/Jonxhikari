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

    return data[0]["url"]


@component.with_command
@tanjun.as_slash_command("kitties", "Fetch a random kitty")
async def kitties_command(ctx: tanjun.abc.Context) -> None:
    if not (url := await call_cat_api(ctx.client)):
        await ctx.respond("Unable to fetch a kitty right now :(")

    else:
        await ctx.respond(url)


@tanjun.as_loader
def load_component(client: SlashClient) -> None:
    client.add_component(component.copy())