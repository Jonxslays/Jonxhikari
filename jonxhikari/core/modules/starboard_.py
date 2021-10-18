import typing as t

import hikari
import tanjun

from jonxhikari import SlashClient, Bot


starboard = tanjun.Component().add_check(lambda ctx: ctx.guild_id is not None)


@starboard.with_message_command
@tanjun.with_author_permission_check(hikari.Permissions.ADMINISTRATOR)
@tanjun.with_argument("channel", converters=tanjun.to_channel)
@tanjun.with_parser
@tanjun.as_message_command("setstarboard")
async def config_starboard(
    ctx: tanjun.abc.MessageContext,
    channel: hikari.TextableGuildChannel,
    bot: Bot = tanjun.injected(type=Bot),
) -> None:
    """Sets the starboard channel for this guild. Requires ADMIN."""

    if channel.type is not hikari.ChannelType.GUILD_TEXT:
        await ctx.respond(
            bot.errors.embed(ctx, "Can only set the stardboard channel to a guild text channel.")
        )
        return 
    #await bot.pool.execute("UPDATE guilds SET StarChannel = $1 WHERE GuildID = $2;", channel.id, )

    await ctx.respond(f"The channel you selected was {channel.mention}")



@tanjun.as_loader
def load_component(client: tanjun.abc.Client) -> None:
    client.add_component(starboard.copy())
