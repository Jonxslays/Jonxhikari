import datetime

from hikari.events.base_events import ExceptionEvent
from hikari.messages import Attachment
import lightbulb
import hikari


class Events(lightbulb.Plugin):
    """Jonxhikaris pseudo event handler."""
    def __init__(self, bot: lightbulb.Bot) -> None:
        self.bot = bot
        super().__init__()

    @lightbulb.plugins.listener()
    async def on_cmd(self, _: lightbulb.CommandCompletionEvent) -> None:
        """Fires on completion of a command"""
        self.bot._invokes += 1

    @lightbulb.plugins.listener()
    async def on_cmd_exc(self, event: lightbulb.CommandErrorEvent) -> None:
        """Handles Lightbulb command exception events."""
        await self.bot.errors.parse(event.exception, event.context)

    @lightbulb.plugins.listener()
    async def on_exc(self, event: ExceptionEvent) -> None:
        """Handles Lightbulb command exception events."""
        await self.bot.errors.parse(event.exception, None)


    @lightbulb.plugins.listener()
    async def on_reaction_add(self, event: hikari.ReactionAddEvent) -> None:
        stars = ("⭐")

        ####################################################
        # THIS IS NOT A WORKING STARBOARD IMPL, DONT COPY IT
        ####################################################

        if event.emoji in stars:
            stars.pop(event.emoji.name)
            if not (user := self.bot.cache.get_user(event.user_id)):
                user = await self.bot.rest.fetch_user(event.user_id)

            if not (message := self.bot.cache.get_message(event.message_id)):
                message = await self.bot.rest.fetch_message(event.channel_id, event.message_id)

            if not user.is_bot: #and user.id != message.author.id:
                # TODO add this back after testing
                # message.author.is_bot and not

                if stars[0] in message.reactions:
                    print("it is")

                if not (channel := self.bot.cache.get_guild_channel(message.channel_id)):
                    channel = await self.bot.rest.fetch_channel(message.channel_id)

                if "starboard" in (_guild := self.bot.guilds[message.guild_id]).keys():
                    print("there is a starboard cache")

                    if not (star_channel := self.bot.cache.get_guild_channel(_guild["starboard"])):
                        star_channel = self.bot.rest.fetch_channel(_guild["starboard"])

                    starcount = await self.bot.db.field(
                        "INSERT INTO starboard (BaseMessageID, GuildID) VALUES (?, ?) ON CONFLICT(BaseMessageID, GuildID) DO UPDATE SET Stars = Stars + 1 RETURNING STARS",
                        message.id, message.guild_id
                    )

                    print(starcount)

                    embed = hikari.Embed(
                        title="Get context...",
                        url=message.link,
                        description=message.content or "See attachment",
                        timestamp=datetime.datetime.now().astimezone(),
                        color=hikari.Color.from_hex_code("#FFDF00")
                    ).set_author(
                        name=message.author.username,
                        icon=message.author.avatar_url or message.author.default_avatar_url
                    ).set_footer(
                        text=f"Last star"
                    )

                    if message.attachments:
                        embed.set_image(message.attachments[0].url)


                    await star_channel.send(f"{event.emoji} **{starcount}** -> <#{channel.id}>", embed=embed)

                else:
                    print("no cache")
                    if not (star_channel := self.bot.cache.get_guild_channel(825219011796533249)):
                        star_channel = self.bot.rest.fetch_channel(825219011796533249)

                    self.bot.guilds[message.guild_id]["starboard"] = star_channel.id

                    starcount = await self.bot.db.field(
                        "INSERT INTO starboard (BaseMessageID, GuildID) VALUES (?, ?) ON CONFLICT(BaseMessageID, GuildID) DO UPDATE SET Stars = Stars + 1 RETURNING STARS",
                        message.id, message.guild_id
                    )

                    print(starcount)

                    embed = hikari.Embed(
                        title="Get context...",
                        url=message.link,
                        description=message.content or "See attachment",
                        timestamp=datetime.datetime.now().astimezone(),
                        color=hikari.Color.from_hex_code("#FFDF00")
                    ).set_author(
                        name=message.author.username,
                        icon=message.author.avatar_url or message.author.default_avatar_url
                    ).set_footer(
                        text=f"Last star"
                    )

                    if message.attachments:
                        embed.set_image(message.attachments[0].url)

                    await star_channel.send(f"{event.emoji} **{starcount}** -> <#{channel.id}>", embed=embed)


            else:
                await message.remove_reaction(emoji=event.emoji, user=user)




def load(bot: lightbulb.Bot) -> None:
    bot.add_plugin(Events(bot))


def unload(bot: lightbulb.Bot) -> None:
    bot.remove_plugin("Events")
