from hikari.events.base_events import ExceptionEvent
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
        stars = ("⭐", "🌟")

        if event.emoji in stars:
            if not (user := self.bot.cache.get_user(event.user_id)):
                user = await self.bot.rest.fetch_user(event.user_id)

            if not (message := self.bot.cache.get_message(event.message_id)):
                message = await self.bot.rest.fetch_message(event.channel_id, event.message_id)

            if not message.author.is_bot and not user.is_bot and user.id != message.author.id:
                print("this triggered")

                if "starboard" in (_guild := self.bot.guilds[message.guild_id]).keys():
                    print("there is a starboard cache")

                    star_channel = self.bot.cache.get_guild_channel(_guild["starboard"])

                    await star_channel.send(f"message: {message.id} starred by: {user} guild: {star_channel.guild_id}")
                    return None

                print("no cache")
                star_channel = self.bot.cache.get_guild_channel(825219011796533249)

                self.bot.guilds[message.guild_id]["starboard"] = star_channel.id

                await star_channel.send(f"message: {message.id} starred by: {user} guild: {star_channel.guild_id}")
                return None

            else:
                await message.remove_reaction(emoji=event.emoji, user=user)

            # TODO Finish this. Correctly triggering on reaction already.



def load(bot: lightbulb.Bot) -> None:
    bot.add_plugin(Events(bot))


def unload(bot: lightbulb.Bot) -> None:
    bot.remove_plugin("Events")
