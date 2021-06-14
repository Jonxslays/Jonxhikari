from sys import exc_info
import typing as t

from lightbulb import errors as le
from hikari import errors as he

import lightbulb
import hikari


class Errors:

    @staticmethod
    async def parse(exc: t.Union[le.CommandError, Exception], ctx: t.Optional[lightbulb.Context]) -> None:
        if isinstance(exc, le.NotEnoughArguments):
            args = "\n".join(f" > {a}" for a in exc.missing_args)
            await ctx.respond(f"**ERROR**\nRequired argument(s) were missing:\n```{args}```")
            raise exc

        elif isinstance(exc, le.MissingRequiredPermission):
            perms = "\n".join(f" > {p.name}" for p in exc.permissions.split()).replace("_", " ")
            await ctx.respond(f"**ERROR**\n{exc.text}.```{perms}```")
            raise exc

        elif isinstance(exc, le.ConverterFailure):
            await ctx.respond(f"**ERROR**\nConversion of arguments failed during `{ctx.command.qualified_name}` command.")
            raise exc

        elif isinstance(exc, Exception):
            print(exc)
            raise exc

        elif isinstance(exc, KeyError):
            print(exc)
            raise exc
