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

    # Returns output for the embed
    def reload_embed(self, mod: str, e: t.Union[Exception, str] = None) -> tuple:
        """Creates a tuple of embed fields based on input.

        Args:
            mod (str): The module being modified.
            e (Exception, optional): The exception if there was one. Defaults to None.

        Returns:
            tuple: with fields for an embed.
        """
        if not e:
            return (
                ("Loaded:", f'```{mod}.py```', True),
                ("Status:", "```SuccessfulSync```", True),
                ("Info:", "```Establishing connection.. \nAwaiting tasks..```", False),
            )
        elif e == "SuccessfulSync":
            return (
                ("Unloaded:", f'```{mod}.py```', True),
                ("Status:", "```SuccessfulSync```", True),
                ("Info:", "```Unhooked.. \nSleeping..```", False),
            ),


    @lightbulb.checks.owner_only()
    @lightbulb.command(name="reload")
    async def reload_cmd(self, ctx: lightbulb.Context, module: str) -> None:
        """This command loads/reloads a Jonxhikari module.

        ```Args:\n
            - ctx: Command context.\n
            - module: Module to reload.```
        """
        pass
        # TODO re-write this command


def load(bot: lightbulb.Bot) -> None:
    bot.add_plugin(Admin(bot))


def unload(bot: lightbulb.Bot) -> None:
    bot.remove_plugin("Admin")
