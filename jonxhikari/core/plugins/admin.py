import re
import typing as t
from hikari.presences import Status

import lightbulb
import hikari
from lightbulb import errors


class Admin(lightbulb.Plugin):
    """Dedicated to Admin only commands."""
    def __init__(self, bot: lightbulb.Bot) -> None:
        self.bot = bot
        super().__init__()

    @lightbulb.checks.has_guild_permissions(
        hikari.Permissions.ADMINISTRATOR,
        hikari.Permissions.MANAGE_GUILD,
    )
    @lightbulb.command(name="prefix")
    async def prefix_cmd(self, ctx: lightbulb.Context, _prefix: t.Optional[str] = None) -> None:
        """View or change Jonxhikari's command prefix."""

        if not _prefix:
            return await ctx.respond(f"The current prefix is `{self.bot.guilds[ctx.guild_id]['prefix']}`.")

        if len(_prefix) > 3:
            return await ctx.respond("The prefix can have a max of 3 characters.")

        self.bot.guilds[ctx.guild_id]["prefix"] = _prefix
        await self.bot.db.execute("UPDATE guilds SET Prefix = ? WHERE GuildID = ?", _prefix, ctx.guild_id)
        await ctx.respond(f"Prefix successfully updated to: `{_prefix}`")


class Owner(lightbulb.Plugin):
    """Dedicated to Owner only commands."""
    def __init__(self, bot: lightbulb.Bot) -> None:
        self.bot = bot
        self.plugin_path = "jonxhikari.core.plugins."
        super().__init__()

    @staticmethod
    def _is_invalid(module: str, path: str) -> list:
        return [
            ("Extension:", f'```{module}.py```', True),
            ("Status:", f"```ExtensionNotFound```", True),
            ("Info:", f"```{path} is not a valid extension.```", False),
        ]

    @staticmethod
    def _already_loaded(module: str, exc: errors.ExtensionError) -> list:
        return [
            ("Extension:", f'```{module}.py```', True),
            ("Status:", f"```{exc.__class__.__name__}```", True),
            ("Info:", f"```{exc.text}```", False),
        ]

    @staticmethod
    def _success(module: str) -> list:
        return [
            ("Extension:", f'```{module}.py```', True),
            ("Status:", "```SuccessfulSync```", True),
            ("Info:", "```Establishing connection..\nAwaiting tasks..```", False),
        ]

    @lightbulb.owner_only()
    @lightbulb.command(name="load")
    async def load_cmd(self, ctx: lightbulb.Context, module: str) -> None:
        """Loads a Jonxhikari module."""

        module = module.lower()
        path = self.plugin_path + module

        if path not in self.bot.extensions:
            fields = self._is_invalid(module, path)

        else:
            try:
                self.bot.load_extension(path)

            except errors.ExtensionAlreadyLoaded as e:
                fields = self._already_loaded(module, e)

            else:
                fields = self._success(module)

        await ctx.respond(
            embed = self.bot.embeds.build(
                ctx = ctx, fields = fields,
                header="Loading..."
            )
        )

    @lightbulb.owner_only()
    @lightbulb.command(name="unload")
    async def unload_cmd(self, ctx: lightbulb.Context) -> None:
        print("unload")

    @lightbulb.owner_only()
    @lightbulb.command(name="reload")
    async def reload_cmd(self, ctx: lightbulb.Context) -> None:
        print("reload")

    @lightbulb.owner_only()
    @lightbulb.command(name="shutdown")
    async def shutdown_cmd(self, ctx: lightbulb.Context) -> None:
        """Gracefully shuts down Jonxhikari."""

        await ctx.message.delete()
        await ctx.respond("Shutting down...")
        await self.bot.close()


def load(bot: lightbulb.Bot) -> None:
    bot.add_plugin(Admin(bot))
    bot.add_plugin(Owner(bot))


def unload(bot: lightbulb.Bot) -> None:
    bot.remove_plugin("Admin")
    bot.remove_plugin("Owner")
