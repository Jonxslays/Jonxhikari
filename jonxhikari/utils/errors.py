import typing as t
import re

from lightbulb import errors as _le
from hikari import errors as _he

import lightbulb
import hikari


class Errors:
    async def parse(self, ctx: lightbulb.Context, exc: lightbulb.errors.CommandError) -> None:
        if isinstance(exc, _le.NotEnoughArguments):
            await ctx.respond(f"Required argument(s) were missing:\n```{exc.missing_args}```")

        elif isinstance(exc, _le.MissingRequiredPermission):
            missing_perms = "\n".join(p.name for p in exc.permissions.split()).replace("_", " ")
            await ctx.respond(f"{exc.text}.```{missing_perms}```")
