import typing as t

from lightbulb import errors as _le
from hikari import errors as _he

import lightbulb
import hikari


class Errors:
    async def parse(self, ctx: lightbulb.Context, exc: Exception) -> None:
        if isinstance(exc, _le.NotEnoughArguments):
            await ctx.respond("One or more required arguments are missing.")
