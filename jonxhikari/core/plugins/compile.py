import asyncio
import re

import lightbulb
import hikari

import jonxhikari

from pprint import pprint


class Compile(lightbulb.Plugin):
    """Runs code through the Piston api."""

    def __init__(self, bot: jonxhikari.Bot) -> None:
        super().__init__()
        self.bot = bot
        self.langs: list[str] = []
        self.uri = "https://emkc.org/api/v2/piston"

    async def get_langs(self) -> None:
        """Gets available language details from Piston api."""
        uri = self.uri + "/runtimes"

        async with self.bot.session.get(uri) as response:
            if not 200 <= response.status <= 299:
                return None

            if not (data := await response.json()):
                return None

        self.resolve_langs(*data)

    def resolve_langs(self, *data: dict[str, str]) -> None:
        """Saves raw language data to cache."""
        for lang in data:
            self.langs.append(lang["language"])
            self.langs.extend(a for a in lang["aliases"])

    @lightbulb.command(name="run")
    async def run_cmd(self, ctx: lightbulb.Context, *, code: str) -> None:
        """Sends code to the Piston api to be executed."""
        uri = self.uri + "/execute"

        if not self.langs:
            await self.get_langs()

        if not (matches := re.match("```(\w+)\s([\w\W]+)[\s*]?```", code)):
            output = f"{await self.bot.resolve_prefix(self.bot, ctx.message)}run \`\`\`python\nprint('This is a test')\`\`\`"
            await ctx.respond(
                f"Wrong format. Use a code block.\nSpecify lang inside first set of triple backticks. Example:\n\n{output}",
                reply=True,
            )
            return None

        lang = matches.group(1)
        source = matches.group(2)

        if lang not in self.langs:
            await ctx.respond(f"{lang} is not a supported language.", reply=True)
            return None

        data = {
            "language": lang,
            "version": "*",
            "files": [{"content": source}],
        }

        async with self.bot.session.post(uri, json=data) as response:
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

            fields.append(("Output:", f"```{stdout}```", False))

        if stderr := data["run"]["stderr"]:
            color = hikari.Color.from_rgb(210, 0, 0)

            fields.append(("Errors:", f"```{stderr}```", False))

        await ctx.respond(
            embed=self.bot.embeds.build(
                ctx=ctx, fields=fields, color=color, header="Source code evaluation results"
            ),
            reply=True,
        )


def load(bot: jonxhikari.Bot) -> None:
    bot.add_plugin(Compile(bot))


def unload(bot: jonxhikari.Bot) -> None:
    bot.remove_plugin("Compile")
