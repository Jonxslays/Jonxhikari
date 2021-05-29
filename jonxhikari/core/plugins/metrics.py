import time

import lightbulb
import hikari


class Metrics(lightbulb.Plugin):
    def __init__(self, bot: lightbulb.Bot) -> None:
        self.bot = bot
        super().__init__()

    @lightbulb.command(name="ping")
    async def ping_cmd(self, ctx: lightbulb.Context) -> None:
        start = time.time()
        msg = await ctx.respond(f"**Latency**: {(latency := self.bot.heartbeat_latency * 1000):.0f} ms")
        await msg.edit(f"**Latency**: {latency:.0f} ms\n**Response**: {((time.time() - start) * 1000):.0f} ms")


def load(bot: lightbulb.Bot) -> None:
    bot.add_plugin(Metrics(bot))


def unload(bot: lightbulb.Bot) -> None:
    bot.remove_plugin("Metrics")
