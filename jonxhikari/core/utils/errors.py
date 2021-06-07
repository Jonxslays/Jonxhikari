import typing as t

from lightbulb import errors as le
from hikari import errors as he

import lightbulb


class Errors:

    @staticmethod
    async def parse(ctx: lightbulb.Context, exc: le.CommandError) -> None:
        if isinstance(exc, le.NotEnoughArguments):
            args = "\n".join(f" > {a}" for a in exc.missing_args)
            await ctx.respond(f"Required argument(s) were missing:\n```{args}```")

        elif isinstance(exc, le.MissingRequiredPermission):
            perms = "\n".join(f" > {p.name}" for p in exc.permissions.split()).replace("_", " ")
            await ctx.respond(f"{exc.text}.```{perms}```")
