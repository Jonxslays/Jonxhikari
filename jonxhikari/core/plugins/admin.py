import typing as t

import lightbulb
import hikari
from lightbulb import errors

import jonxhikari


class Admin(lightbulb.Plugin):
    """Dedicated to Admin only commands."""

    def __init__(self, bot: jonxhikari.Bot) -> None:
        self.bot = bot
        super().__init__()

    @lightbulb.check(
        lightbulb.has_guild_permissions(
            hikari.Permissions.ADMINISTRATOR,
        )
    )
    @lightbulb.command(name="prefix")
    async def prefix_cmd(self, ctx: lightbulb.Context, _prefix: t.Optional[str] = None) -> None:
        """View or change Jxhk's command prefix."""
        if not _prefix:
            await ctx.respond(
                f"The current prefix is `{self.bot.guilds[ctx.guild_id]['prefix']}`."
            )
            return None

        if len(_prefix) > 3:
            await ctx.respond("The prefix can have a max of 3 characters.")
            return None

        self.bot.guilds[ctx.guild_id]["prefix"] = _prefix
        await self.bot.pool.execute(
            "UPDATE guilds SET Prefix = $1 WHERE GuildID = $2;", _prefix, ctx.guild_id
        )
        await ctx.respond(f"Prefix successfully updated to: `{_prefix}`")


class Owner(lightbulb.Plugin):
    """Dedicated to Owner only commands."""

    def __init__(self, bot: jonxhikari.Bot) -> None:
        self.bot = bot
        self.plugin_path = "jonxhikari.core.plugins."
        super().__init__()

    @staticmethod
    def is_invalid(module: str) -> list[tuple[str, str, bool]]:
        return [
            ("Extension:", f"```{module}.py```", True),
            ("Status:", f"```ExtensionNotFound```", True),
            ("Info:", f"```{module} is not a valid extension.```", False),
        ]

    @staticmethod
    def failed_attempt(module: str, exc: errors.ExtensionError) -> list[tuple[str, str, bool]]:
        return [
            ("Extension:", f"```{module}.py```", True),
            ("Status:", f"```{exc.__class__.__name__}```", True),
            ("Info:", f"```{exc.text}```", False),
        ]

    @staticmethod
    def success(module: str, action: str) -> list[tuple[str, str, bool]]:
        return [
            ("Extension:", f"```{module}.py```", True),
            ("Status:", "```SuccessfulSync```", True),
            ("Info:", f"```{module} {action}```", False),
        ]

    @lightbulb.check(lightbulb.owner_only)
    @lightbulb.command(name="load")
    async def load_cmd(self, ctx: lightbulb.Context, module: str) -> None:
        """Loads a Jxhk plugin."""
        module = module.lower()
        path = self.plugin_path + module

        if module not in self.bot._plugins:
            fields = self.is_invalid(module)

        else:
            try:
                self.bot.load_extension(path)

            except errors.ExtensionAlreadyLoaded:
                self.bot.reload_extension(path)
                fields = self.success(module, "reloaded.\nlistening...")

            else:
                fields = self.success(module, "loaded.\nlistening...")

        await ctx.respond(embed=self.bot.embeds.build(ctx=ctx, fields=fields, header="Loading..."))

    @lightbulb.check(lightbulb.owner_only)
    @lightbulb.command(name="unload")
    async def unload_cmd(self, ctx: lightbulb.Context, module: str) -> None:
        """Unloads a Jonxhikari module."""
        module = module.lower()
        path = self.plugin_path + module

        if path not in self.bot.extensions:
            fields = self.is_invalid(module)

        else:
            try:
                self.bot.unload_extension(path)

            except errors.ExtensionNotLoaded as e:
                fields = self.failed_attempt(module, e)

            else:
                fields = self.success(module, "unloaded.\nsleeping...")

        await ctx.respond(
            embed=self.bot.embeds.build(ctx=ctx, fields=fields, header="Unloading...")
        )

    @lightbulb.check(lightbulb.owner_only)
    @lightbulb.command(name="shutdown")
    async def shutdown_cmd(self, ctx: lightbulb.Context) -> None:
        """Gracefully shuts down Jxhk."""
        await ctx.message.delete()
        await ctx.respond("Shutting down...")
        await self.bot.close()


def load(bot: jonxhikari.Bot) -> None:
    bot.add_plugin(Admin(bot))
    bot.add_plugin(Owner(bot))


def unload(bot: jonxhikari.Bot) -> None:
    bot.remove_plugin("Admin")
    bot.remove_plugin("Owner")
