import asyncio
import typing as t

import lightbulb
import hikari


class Tags(lightbulb.Plugin):
    """Handles Jonxhikari's tag system"""
    def __init__(self, bot: lightbulb.Bot) -> None:
        self.reserved = ("create", "delete", "edit", "info", "list", "transfer")
        self.bot = bot
        super().__init__()

    @lightbulb.group(name="tag")
    async def tag_group(self, ctx: lightbulb.Context, name: t.Optional[str]) -> None:
        """Command group for managing guild specific tags."""
        if content := await self.bot.db.field(
            "UPDATE tags SET Uses = Uses + 1 WHERE GuildID = ? AND TagName = ? RETURNING TagContent",
            ctx.guild_id, name.lower()
        ):
            await ctx.respond(content, reply=True)
            return None

        await ctx.respond(f"`{name}` is not a valid tag.", reply=True)

    @tag_group.command(name="create")
    async def tag_create_cmd(self, ctx: lightbulb.Context, name: str, *, content: str) -> None:
        """Command for creating a new tag."""
        if (name := name.lower()) in self.reserved:
            await ctx.respond(
                f"That tag name is reserved. All of these are: ```{', '.join(self.reserved)}```", reply=True
            )
            return None

        # If someone tries to make an already made tag... yeah thats a use
        if owner := await self.bot.db.field(
            "UPDATE tags SET Uses = Uses + 1 WHERE GuildID = ? AND TagName = ? RETURNING TagOwner",
            ctx.guild_id, name
        ):
            await ctx.respond(
                f"Sorry, `{name}` was already created by {self.bot.cache.get_member(ctx.guild_id, owner).mention}." +
                "Try a different tag name.", reply=True
            )
            return None

        # Good to go ahead and make the new tag
        await self.bot.db.execute(
            "INSERT INTO tags (GuildID, TagOwner, TagName, TagContent) VALUES (?, ?, ?, ?)",
            ctx.guild_id, ctx.author.id, name, content
        )
        await ctx.respond(f"**SUCCESS**\n`{name}` tag created by {ctx.author.mention}.", reply=True)

    @tag_group.command(name="edit")
    async def tag_edit_cmd(self, ctx: lightbulb.Context, name: str, *, content: str) -> None:
        """Command for editing a tag you own."""
        name = name.lower()

        if owner := await self.bot.db.field(
            "SELECT TagOwner FROM tags WHERE GuildID = ? AND TagName = ?",
            ctx.guild_id, name
        ):
            # A successful edit
            if owner == ctx.author.id:
                await self.bot.db.execute(
                    "UPDATE tags SET TagContent = ? WHERE TagName = ? AND GuildID = ?",
                    content, name, ctx.guild_id
                )
                await ctx.respond(f"**SUCCESS**\n`{name}` tag edited by {ctx.author.mention}.", reply=True)
                return None

            # Author doesn't own the tag
            await ctx.respond(
                f"**FAILED**\n{self.bot.cache.get_member(ctx.guild_id, owner)} owns the `{name}` tag, not you."
            )
            return None

        # Define emojis
        yes = ":yes:853792470651502603"
        no = ":no:853792496118267954"

        # There is no tag, do they want to make one?
        msg = await ctx.respond(f"**FAILED**\nNo `{name}` tag has been created yet.\nWould you like to create it now?")
        await msg.add_reaction(yes)
        await msg.add_reaction(no)

        def check(e: hikari.ReactionAddEvent) -> bool:
            return e.message_id == msg.id and e.user_id == ctx.author.id and str(e.emoji) in ("yes", "no")

        try:
            e = await self.bot.wait_for(hikari.ReactionAddEvent, 30, check)

        except asyncio.TimeoutError:
            await msg.edit(content=f"**FAILED**\nNo `{name}` tag has been created yet.")
            await msg.remove_all_reactions()

        else:
            # They don't want to make a new tag
            if str(e.emoji) == "no":
                await msg.edit(content=f"**FAILED**\nNo `{name}` tag has been created yet.")
                await msg.remove_all_reactions()

            # They do want to make a new tag
            elif str(e.emoji) == "yes":
                await self.bot.db.execute(
                    "INSERT INTO tags (GuildID, TagOwner, TagName, TagContent) VALUES (?, ?, ?, ?)",
                    ctx.guild_id, ctx.author.id, name, content
                )
                await msg.edit(content=f"**SUCCESS**\n`{name}` tag created by {ctx.author.mention}.", user_mentions=False)
                await msg.remove_all_reactions()

    @tag_group.command(name="transfer")
    async def tag_transfer_cmd(self, ctx: lightbulb.Context, name: str, member: hikari.Member) -> None:
        """Command for transferring a tag you own to someone else."""
        await ctx.respond("subcommand transfer is not yet implemented.")

    @tag_group.command(name="delete")
    async def tag_delete_cmd(self, ctx: lightbulb.Context, name: str) -> None:
        """Command for deleting a tag you own."""
        await ctx.respond("subcommand delete is not yet implemented.")


def load(bot: lightbulb.Bot) -> None:
    bot.add_plugin(Tags(bot))


def unload(bot: lightbulb.Bot) -> None:
    bot.remove_plugin("Tags")
