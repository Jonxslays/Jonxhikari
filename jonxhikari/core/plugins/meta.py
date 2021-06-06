import time

import lightbulb
import hikari


class Meta(lightbulb.Plugin):
    def __init__(self, bot: lightbulb.Bot) -> None:
        self.bot = bot
        super().__init__()

    @lightbulb.command(name="ping")
    async def ping_cmd(self, ctx: lightbulb.Context) -> None:
        """Returns the bots gateway and rest latency."""

        start = time.time()
        msg = await ctx.respond(f"init message")
        end = time.time()

        await msg.edit(f"**Gateway**: {self.bot.heartbeat_latency * 1000:,.0f} ms\n**REST**: {(end - start) * 1000:,.0f} ms")


def load(bot: lightbulb.Bot) -> None:
    bot.add_plugin(Meta(bot))


def unload(bot: lightbulb.Bot) -> None:
    bot.remove_plugin("Meta")
