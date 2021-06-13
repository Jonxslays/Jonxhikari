import distro
from datetime import datetime, timedelta
from platform import python_version
from psutil import Process, virtual_memory
from time import time

import hikari
import lightbulb

from jonxhikari.core.utils import Lines


class Meta(lightbulb.Plugin):
    """Devoted to meta stats etc."""
    def __init__(self, bot: lightbulb.Bot) -> None:
        self.bot = bot
        self.lines = Lines()
        super().__init__()

    @lightbulb.command(name="ping")
    async def ping_cmd(self, ctx: lightbulb.Context) -> None:
        """Returns the bots gateway and rest latency."""
        start = time()
        msg = await ctx.respond("uwu-owo", reply=True)
        end = time()

        await msg.edit(
            f"**Gateway**: {self.bot.heartbeat_latency * 1000:,.0f} ms\n**REST**: {(end - start) * 1000:,.0f} ms",
            user_mentions=False
        )

    @lightbulb.command(name="stats")
    async def stats_cmd(self, ctx: lightbulb.Context) -> None:
        """Displays system info for Jonxhikari"""
        await ctx.message.delete()
        self.lines.count()

        proc = Process()
        with proc.oneshot():
            uptime = str(timedelta(seconds=time() - proc.create_time()))
            cpu_time = str(timedelta(seconds=(cpu := proc.cpu_times()).system + cpu.user))
            mem_total = virtual_memory().total / (1024 ** 2)
            mem_of_total = proc.memory_percent()
            mem_usage = mem_total * (mem_of_total / 100)

        distro_ = distro.linux_distribution(full_distribution_name=False)
        code_p, docs_p, blank_p = self.lines.grab_percents()

        fields = [
            ("Jonxhikari", f"```{self.bot.version}```", True),
            ("Python", f"```{python_version()}```", True),
            ("Hikari", f"```{hikari.__version__}```", True),
            ("Users here", f"```{len(self.bot.cache.get_members_view_for_guild(ctx.guild_id)):,}```", True),
            ("Total users", f"```{len(self.bot.cache.get_users_view()):,}```", True),
            ("Servers", f"```{len(self.bot.guilds):,}```", True),
            ("Lines of code", f"```{self.lines.total:,}```", True),
            ("Latency", f"```{self.bot.heartbeat_latency * 1000:,.0f} ms```", True),
            ("Platform", f"```{distro_[0].title()} {distro_[1]}```", True),
            ("Code breakdown", f"```| {code_p:>5.2f}% | Code  -> {self.lines.code:>6} |\n| {docs_p:>5.2f}% | Docs  -> {self.lines.docs:>6} |\n| {blank_p:>5.2f}% | Blank -> {self.lines.blank:>6} |```", False),
            ("Memory usage", f"```| {mem_of_total:>5,.2f}% | {mem_usage:,.0f} MiB / {(mem_total / 1024):,.0f} GiB |```", False),
            ("Uptime", f"```{uptime}```", True),
            ("CPU time", f"```{cpu_time}```", True)
        ]

        await ctx.respond(
            embed=self.bot.embeds.build(
                ctx=ctx, header=" ", title="System stats",
                thumbnail=self.bot.me.avatar_url,
                fields=fields
            ),
        )


def load(bot: lightbulb.Bot) -> None:
    bot.add_plugin(Meta(bot))


def unload(bot: lightbulb.Bot) -> None:
    bot.remove_plugin("Meta")
