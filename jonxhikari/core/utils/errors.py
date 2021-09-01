import typing as t

from lightbulb import errors as le
from hikari import errors as he

import lightbulb
import hikari
import tanjun


class WTFError(Exception):
    pass


class Errors:
    @staticmethod
    def wtf(message: str) -> WTFError:
        return WTFError(message)

    @staticmethod
    async def parse(exc: Exception) -> None:
        print(exc)
        raise exc

    @staticmethod
    async def parse_tanjun(
        exc: t.Union[tanjun.CommandError, Exception],
        ctx: tanjun.abc.Context
    ) -> None:
        if isinstance(exc, (tanjun.NotEnoughArgumentsError, tanjun.TooManyArgumentsError)):
            await ctx.respond(f"**ERROR**```{exc.message}```")
            raise exc

        elif isinstance(exc, tanjun.MissingDependencyError):
            await ctx.respond(f"**ERROR**```{exc.message}```")
            raise exc

        else:
            print(exc)
            raise exc


    @staticmethod
    async def parse_lightbulb(
        exc: t.Union[le.CommandError, Exception],
        ctx: lightbulb.Context
    ) -> None:
        if isinstance(exc, le.CommandNotFound):
            pass

        elif isinstance(exc, le.NotEnoughArguments):
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

        else:
            print(exc)
            raise exc
