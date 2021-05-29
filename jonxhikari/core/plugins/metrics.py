import lightbulb
import hikari


class Metrics(lightbulb.Plugin):
    def __init__(self, bot: lightbulb.Bot) -> None:
        self.bot = bot
        self.plugin_path = "jonxhikari.bot.plugins."
        super().__init__()




    @lightbulb.command(name="ping")
    async def ping_cmd(self, ctx: lightbulb.Context) -> None:
        await ctx.respond(latency := f"{(self.bot.heartbeat_latency * 1000):.1f} ms")


def load(bot: lightbulb.Bot) -> None:
    bot.add_plugin(Metrics(bot))


def unload(bot: lightbulb.Bot) -> None:
    bot.remove_plugin("Metrics")
