import typing as t

import lightbulb
import hikari


class Admin(lightbulb.Plugin):
    def __init__(self, bot: lightbulb.Bot) -> None:
        self.bot = bot
        self.plugin_path = "jonxhikari.core.plugins."
        super().__init__()

    # Change or view the current guild prefix
    @lightbulb.checks.has_guild_permissions(
        hikari.Permissions.ADMINISTRATOR,
        hikari.Permissions.MANAGE_GUILD,
    )
    @lightbulb.command(name="prefix")
    async def prefix_cmd(self, ctx: lightbulb.Context, _prefix: t.Optional[str] = None) -> None:
        """Change or view the my prefix in your server.

        ```Args:\n
            - ctx: Command context.\n
            - prefix (optional): The new prefix you want. Defaults to None.```
        """
        if not _prefix:
            return await ctx.respond(f"The current prefix is `{self.bot.guilds[ctx.guild_id]['prefix']}`.")

        if len(_prefix) > 3:
            return await ctx.respond("The prefix can have a max of 3 characters.")

        self.bot.guilds[ctx.guild_id]["prefix"] = _prefix
        await self.bot.db.execute("UPDATE guilds SET Prefix = ? WHERE GuildID = ?", _prefix, ctx.guild_id)
        await ctx.respond(f"Prefix successfully updated to: `{_prefix}`")

    # Gracefully shuts down the bot
    @lightbulb.checks.owner_only()
    @lightbulb.command(name="shutdown")
    async def shutdown_cmd(self, ctx: lightbulb.Context) -> None:
        """Shuts down Jonxhikari.

        ```Args:\n
            - ctx: Command context.```
        """

        await ctx.message.delete()
        await ctx.respond("Shutting down...")
        await self.bot.close()


def load(bot: lightbulb.Bot) -> None:
    bot.add_plugin(Admin(bot))


def unload(bot: lightbulb.Bot) -> None:
    bot.remove_plugin("Admin")
