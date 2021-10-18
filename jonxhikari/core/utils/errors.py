import typing as t

import lightbulb
import hikari
import tanjun
from lightbulb import errors as lb_errors

from .embeds import Embeds

DualCtxT = t.Union[lightbulb.Context, tanjun.abc.Context]


class WTFError(Exception):
    pass


class Errors:
    embeds = Embeds()

    def embed(self, ctx: DualCtxT, message: str) -> hikari.Embed:
        embed = self.embeds.build(
            ctx=ctx,
            description=message,
            footer="BYPASS",
        )

        return embed

    @staticmethod
    def wtf(message: str) -> WTFError:
        return WTFError(message)

    @staticmethod
    async def parse(exc: Exception) -> None:
        print(exc)
        raise exc

    async def parse_tanjun(
        self, exc: t.Union[tanjun.CommandError, Exception], ctx: tanjun.abc.Context
    ) -> None:
        if isinstance(exc, (tanjun.NotEnoughArgumentsError, tanjun.TooManyArgumentsError)):
            await ctx.respond(self.embed(ctx, f"**ERROR**```{exc.message}```"))
            raise exc

        elif isinstance(exc, tanjun.MissingDependencyError):
            await ctx.respond(self.embed(ctx, f"**ERROR**```{exc.message}```"))
            raise exc

        else:
            print(exc)
            raise exc

    async def parse_lightbulb(
        self, exc: t.Union[lb_errors.CommandError, Exception], ctx: lightbulb.Context
    ) -> None:
        if isinstance(exc, lb_errors.CommandNotFound):
            pass

        elif isinstance(exc, lb_errors.NotEnoughArguments):
            args = "\n".join(f" > {a}" for a in exc.args[1])
            await ctx.respond(
                self.embed(ctx, f"**ERROR**\nRequired argument(s) were missing:\n```{args}```")
            )
            raise exc

        elif isinstance(exc, lb_errors.MissingRequiredPermission):
            perms = "\n".join(f" > {p}" for p in exc.args[1:]).replace("_", " ")
            await ctx.respond(self.embed(ctx, f"**ERROR**\nMissing permissions.```{perms}```"))
            raise exc

        elif isinstance(exc, lb_errors.ConverterFailure):
            await ctx.respond(
                self.embed(
                    ctx,
                    (
                        "**ERROR**\nConversion of arguments failed during "
                        f"`{ctx.command.qualified_name}` command."
                    ),
                )
            )
            raise exc

        else:
            print(exc)
            raise exc
