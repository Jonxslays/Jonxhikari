import lightbulb
import hikari


# TODO build embed utils
def reload_embed(mod, e = None):
    if not e or e is lightbulb.errors.ExtensionNotLoaded:
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


class Test(lightbulb.Plugin):
    def __init__(self, bot: lightbulb.Bot):
        self.bot = bot
        self.plugin_path = "jonxhikari.bot.plugins."
        super().__init__()

    @lightbulb.command(name="ping")
    async def ping_cmd(self, ctx):
        await ctx.respond(latency := f"{(self.bot.heartbeat_latency * 1000):.0f} ms")
        await ctx.channel.send("testing the send method")

    @lightbulb.command(name="reload")
    async def reload_cmd(self, ctx, mod):
        if not mod:
            return await ctx.respond("Sorry you have to include a module to reload.")

        embed = hikari.Embed()

        try:
            self.bot.reload_extension(self.plugin_path + mod)

        except KeyError as e:
            fields = reload_embed(mod, e)

        except lightbulb.errors.ExtensionNotLoaded as e:
            self.bot.load_extension(self.plugin_path + mod)
            fields = reload_embed(mod, e)

        else:
            fields = reload_embed(mod)

        finally:
            for name, value, inline in fields:
                embed.add_field(name=name, value=value, inline=inline)

            await ctx.respond(embed=embed)


def load(bot):
    bot.add_plugin(Test(bot))

def unload(bot):
    bot.remove_plugin("Test")