import typing as t
import re

from lightbulb import errors as _le
from hikari import errors as _he

import lightbulb


class Errors:

    @staticmethod
    async def parse(ctx: lightbulb.Context, exc: lightbulb.errors.CommandError) -> None:
        if isinstance(exc, _le.NotEnoughArguments):
            args = "\n".join(f" > {a}" for a in exc.missing_args)
            await ctx.respond(f"Required argument(s) were missing:\n```{args}```")

        elif isinstance(exc, _le.MissingRequiredPermission):
            perms = "\n".join(f" > {p.name}" for p in exc.permissions.split()).replace("_", " ")
            await ctx.respond(f"{exc.text}.```{perms}```")
