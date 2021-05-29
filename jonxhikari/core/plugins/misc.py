import lightbulb
import hikari
import time


class Misc(lightbulb.Plugin):
    def __init__(self, bot: lightbulb.Bot) -> None:
        self.bot = bot
        self.plugin_path = "jonxhikari.bot.plugins."
        super().__init__()

    @lightbulb.command(name="go")
    async def go_cmd(self, ctx: lightbulb.Context) -> None:
        start = time.time()
        msg = await ctx.respond("**Latency**: " + (latency := f"{(self.bot.heartbeat_latency * 1000):.0f} ms"))
        await msg.edit(f"**Latency**: {latency}\n**Response**: {((time.time() - start) * 1000):.0f} ms")


def load(bot: lightbulb.Bot) -> None:
    bot.add_plugin(Misc(bot))


def unload(bot: lightbulb.Bot) -> None:
    bot.remove_plugin("Misc")
