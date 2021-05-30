from jonxhikari.core.utils.embeds import Embeds
import typing as t

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
        """View or change Jonxhikari's command prefix.

        Args:
            ctx (lightbulb.Context): Command context.
            _prefix (t.Optional[str], optional): New prefix. Defaults to None.
        """

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


    @lightbulb.owner_only()
    @lightbulb.command(name="load")
    async def load_cmd(self, ctx: lightbulb.Context, module: str) -> None:
        """Loads a Jonxhikari modules.

        Args:
            ctx (lightbulb.Context): Command context.
            module (str): Module to be loaded.
        """

        mod_lower = module.lower()

        try:
            self.bot.load_extension(f"{self.plugin_path}{mod_lower}")

        except errors.ExtensionAlreadyLoaded as e:
            fields = [
                ("Failed:", f'```{mod_lower}.py```', True),
                ("Status:", f"```{e.__class__.__name__}```", True),
                ("Info:", f"```{e.text}```", False),
            ]

        else:
            fields = [
                ("Loaded:", f'```{mod_lower}.py```', True),
                ("Status:", "```SuccessfulSync```", True),
                ("Info:", "```Establishing connection..\nAwaiting tasks..```", False),
            ]

        finally:
            await ctx.respond(
                embed = self.bot.embeds.build(
                    ctx = ctx, fields = fields,
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
        """Gracefully shuts down Jonxhikari.

        Args:
            ctx: (lightbulb.Context): Command context.
        """

        await ctx.message.delete()
        await ctx.respond("Shutting down...")
        await self.bot.close()


def load(bot: lightbulb.Bot) -> None:
    bot.add_plugin(Admin(bot))
    bot.add_plugin(Owner(bot))


def unload(bot: lightbulb.Bot) -> None:
    bot.remove_plugin("Admin")
    bot.remove_plugin("Owner")
