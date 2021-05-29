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
        await ctx.message.delete()
        await ctx.respond("Shutting down...")
        await self.bot.close()

    # Returns output for the embed
    def reload_embed(self, mod: str, e: Exception = None) -> tuple:
        if not e:
            return (
                ("Loaded:", f'```{mod}.py```', True),
                ("Status:", "```SuccessfulSync```", True),
                ("Info:", "```Establishing connection..\nAwaiting tasks..```", False),
            )

        return (
            ("Failed:", f'```{mod}.py```', True),
            ("Status:", f"```{e.__class__.__name__}```", True),
            ("Info:", f"```{e} is not a real module.```", False),
        )

    @lightbulb.checks.owner_only()
    @lightbulb.command(name="reload")
    async def reload_cmd(self, ctx: lightbulb.Context, mod: str) -> None:
        if not mod:
            return await ctx.respond("Sorry you have to include a module to reload.")

        embed = hikari.Embed()

        try:
            self.bot.reload_extension(self.plugin_path + mod)

        except KeyError as e:
            fields = self.reload_embed(mod, e)

        except lightbulb.errors.ExtensionNotLoaded:
            self.bot.load_extension(self.plugin_path + mod)
            fields = self.reload_embed(mod)

        else:
            fields = self.reload_embed(mod)

        finally:
            for name, value, inline in fields:
                embed.add_field(name=name, value=value, inline=inline)

            await ctx.respond(embed=embed)


def load(bot: lightbulb.Bot) -> None:
    bot.add_plugin(Admin(bot))


def unload(bot: lightbulb.Bot) -> None:
    bot.remove_plugin("Admin")
