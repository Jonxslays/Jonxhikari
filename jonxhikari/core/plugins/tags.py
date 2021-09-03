import asyncio

import lightbulb
import hikari

import jonxhikari


class Tags(lightbulb.Plugin):
    """Handles Jonxhikari's tag system"""
    def __init__(self, bot: jonxhikari.Bot) -> None:
        self.reserved = ("create", "delete", "edit", "info", "list", "transfer")
        self.bot = bot
        super().__init__()

    @lightbulb.group(name="tag")
    async def tag_group(self, ctx: lightbulb.Context, name: str) -> None:
        """Command group for managing guild specific tags."""
        if content := await self.bot.db.field(
            "UPDATE tags SET Uses = Uses + 1 WHERE GuildID = ? AND TagName = ? RETURNING TagContent",
            ctx.guild_id, name.lower()
        ):
            await ctx.respond(content, reply=True)
            return None

        await ctx.respond(f"`{name}` is not a valid tag.", reply=True)

    @tag_group.command(name="list")
    async def tag_list_cmd(self, ctx: lightbulb.Context) -> None:
        """Command for listing all tags."""
        query = "SELECT TagName from tags WHERE GuildID = ?"

        if len(tags := await self.bot.db.column(query, ctx.guild_id)) == 0:
            await ctx.respond("No tags for this guild yet, make one!", reply=True)
            return None

        description: str = ', '.join(str(t) for t in tags)

        await ctx.respond(f"```{description}```")

    @tag_group.command(name="create")
    async def tag_create_cmd(self, ctx: lightbulb.Context, name: str, *, content: str) -> None:
        """Command for creating a new tag."""
        if (name := name.lower()) in self.reserved:
            await ctx.respond(
                f"That tag name is reserved. All of these are: ```{', '.join(self.reserved)}```", reply=True
            )
            return None

        # If someone tries to make an already made tag... yeah thats a use :kek:
        if owner := await self.bot.db.field(
            "UPDATE tags SET Uses = Uses + 1 WHERE GuildID = ? AND TagName = ? RETURNING TagOwner",
            ctx.guild_id, name
        ):
            await ctx.respond(
                f"**FAILURE**\nSorry, `{name}` was already created by {ctx.author.mention}. "
                "Try a different tag name.", reply=True
            )
            return None

        # A successful tag creation
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
            # A successful tag edit
            if owner == ctx.author.id:
                await self.bot.db.execute(
                    "UPDATE tags SET TagContent = ? WHERE TagName = ? AND GuildID = ?",
                    content, name, ctx.guild_id
                )
                await ctx.respond(f"**SUCCESS**\n`{name}` tag edited by {ctx.author.mention}.", reply=True)
                return None

            # Author doesn't own the tag
            await ctx.respond(
                f"**FAILURE**\n{self.bot.cache.get_member(ctx.guild_id, owner)} owns the `{name}` tag, not you."
            )
            return None

        # Define emojis
        yes = 853792470651502603
        no = 853792496118267954

        # There is no tag with that name, do they want to make one?
        msg = await ctx.respond(f"**WARNING**\nNo `{name}` tag exists. Would you like to create it now?")
        await msg.add_reaction("yes", yes)
        await msg.add_reaction("no", no)

        def predicate(e: hikari.ReactionAddEvent) -> bool:
            return e.message_id == msg.id and e.user_id == ctx.author.id and e.emoji_id in (yes, no)

        try:
            e = await self.bot.wait_for(hikari.ReactionAddEvent, 30, predicate)

        except asyncio.TimeoutError:
            await msg.edit(content=f"**TIMEOUT FAILURE**\nNo `{name}` tag exists.")
            await msg.remove_all_reactions()

        else:
            # They don't want to make a new tag
            if e.emoji_id == no:
                await msg.edit(content=f"**ABORTED**\nNot creatomg new tag `{name}`.")
                await msg.remove_all_reactions()

            # They do want to make a new tag
            elif e.emoji_id == yes:
                await self.bot.db.execute(
                    "INSERT INTO tags (GuildID, TagOwner, TagName, TagContent) VALUES (?, ?, ?, ?)",
                    ctx.guild_id, ctx.author.id, name, content
                )
                await msg.edit(
                    content=f"**SUCCESS**\n`{name}` tag created by {ctx.author.mention}.", user_mentions=False
                )
                await msg.remove_all_reactions()

    @tag_group.command(name="transfer")
    async def tag_transfer_cmd(self, ctx: lightbulb.Context, name: str, member: hikari.Member) -> None:
        """Command for transferring a tag you own to someone else."""
        name = name.lower()

        if owner := await self.bot.db.field(
            "SELECT TagOwner FROM tags WHERE GuildID = ? AND TagName = ?", ctx.guild_id, name
        ):
            # A successful transfer
            if owner == ctx.author.id:
                await self.bot.db.execute(
                    "UPDATE tags SET TagOwner = ? WHERE GuildID = ? and TagName = ?",
                    member.id, ctx.guild_id, name
                )
                await ctx.respond(
                    f"**SUCCESS**\n`{name}` tag transferred from {ctx.author.mention} to {member.mention}.",
                    reply=True
                )
                return None

            # Can't transfer a tag they don't own
            await ctx.respond(
                f"**FAILURE**\n<@!{owner}> owns the `{name}` tag, not you.",
                reply=True
            )
            return None

        # Can't transfer a tag that doesn't exist
        await ctx.respond(f"**FAILURE**\nNo `{name}` tag exists.", reply=True)

    @tag_group.command(name="delete")
    async def tag_delete_cmd(self, ctx: lightbulb.Context, name: str) -> None:
        """Command for deleting a tag you own."""
        name = name.lower()

        if owner := await self.bot.db.field(
            "SELECT TagOwner FROM tags WHERE GuildID = ? AND TagName = ?", ctx.guild_id, name
        ):
            # A successful deletion
            if owner == ctx.author.id:
                await self.bot.db.execute(
                    "DELETE FROM tags WHERE GuildID = ? and TagName = ?", ctx.guild_id, name
                )
                await ctx.respond(f"**SUCCESS**\n`{name}` tag deleted by {ctx.author.mention}.", reply=True)
                return None

            # Can't delete a tag they don't own
            await ctx.respond(
                f"**FAILURE**\n<@!{owner}> owns the `{name}` tag, not you.",
                reply=True
            )
            return None

        # Can't delete a tag that doesn't exist
        await ctx.respond(f"**FAILURE**\nNo `{name}` tag exists.", reply=True)


def load(bot: jonxhikari.Bot) -> None:
    bot.add_plugin(Tags(bot))


def unload(bot: jonxhikari.Bot) -> None:
    bot.remove_plugin("Tags")
