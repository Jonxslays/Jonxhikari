import re

import aiohttp
import asyncio
import lightbulb
import hikari

from pprint import pprint

class Compile(lightbulb.Plugin):
    def __init__(self, bot: lightbulb.Bot) -> None:
        super().__init__()
        self.bot = bot
        self.langs = []
        self.uri = "https://emkc.org/api/v2/piston"

    async def get_langs(self) -> None:
        """Gets available language details from Piston api."""

        uri = self.uri + "/runtimes"

        async with aiohttp.ClientSession() as session:
            async with session.get(uri) as response:
                if not 200 <= response.status <= 299:
                    return None

                if not (data := await response.json()):
                    return None

        await asyncio.gather(
            *(self.resolve_lang(lang) for lang in data)
        )

    async def resolve_lang(self, data: dict) -> None:
        """Saves raw language data to memory."""

        self.langs.append(data["language"])

        for a in data["aliases"]:
            self.langs.append(a)

    @lightbulb.command(name="run")
    async def run_cmd(self, ctx: lightbulb.Context, *, code: str) -> None:
        """Sends code to the Piston api to be executed."""

        uri = self.uri + "/execute"

        if not self.langs:
            await self.get_langs()

        if not (matches := re.match("\`\`\`(\w+)\s([\w\W]+)[\s*]?\`\`\`", code)):
            await ctx.respond("Wrong format. Use a code block. Specify lang inside first set of triple backticks.")
            return None

        lang = matches.groups()[0]
        source = matches.groups()[1]

        if lang not in self.langs:
            await ctx.respond(f"{lang} is not a supported language.")
            return None

        data = {
            "language": lang,
            "version": "*",
            "files": [
                { "content": source }
            ],
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(uri, json=data) as response:
                if not 200 <= response.status <= 299:
                    return None

                if not (data := await response.json()):
                    return None

        fields = [
            ("Language:", f"```{data['language'].title()}```", True),
            ("Version:", f"```{data['version']}```", True),
        ]

        if stdout := data["run"]["stdout"]:
            color = hikari.Color.from_rgb(0, 210, 0)

            fields.append(
                ("Output:", f"```{stdout}```", False)
            )

        if stderr := data["run"]["stderr"]:
            color = hikari.Color.from_rgb(210, 0, 0)

            fields.append(
                ("Errors:", f"```{stderr}```", False)
            )

        await ctx.respond(
            embed = self.bot.embeds.build(
                ctx=ctx, fields=fields, color=color,
                header="Source code evaluation results"
            )
        )


def load(bot: lightbulb.Bot) -> None:
    bot.add_plugin(Compile(bot))


def unload(bot: lightbulb.Bot) -> None:
    bot.remove_plugin("Compile")
