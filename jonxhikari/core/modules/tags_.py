import asyncio
import typing as t

import hikari
import tanjun

from jonxhikari import SlashClient


component = tanjun.Component()


RESERVED_TAGS = (
    "create",
    "delete",
    "edit",
    "info",
    "list",
    "transfer",
    "get",
)


tag_group = component.with_slash_command(
    tanjun.SlashCommandGroup("tag", "Slash command group related to tags.")
).add_check(lambda ctx: ctx.guild_id is not None)


@tag_group.with_command
@tanjun.with_str_slash_option("name", "The name of the tag to get.")
@tanjun.as_slash_command("get", "Gets a tag from the database.")
async def tag_get_slash_command(ctx: tanjun.abc.Context, name: str) -> None:
    """Gets a tag from the database."""
    assert isinstance(ctx.client, SlashClient)
    query = "UPDATE tags SET Uses = Uses + 1 WHERE GuildID = $1 AND TagName = $2 RETURNING TagContent;"

    if content := await ctx.client.bot.pool.fetch(query, ctx.guild_id, name.lower()):
        await ctx.respond(content)
        return None

    await ctx.respond(
        ctx.client.errors.embed(ctx, f"`{name}` is not a valid tag.")
    )


@tag_group.with_command
@tanjun.with_member_slash_option("member", "The member to get tags for.", default=None)
@tanjun.with_str_slash_option("name", "The name of the tag to get.", default=None)
@tanjun.as_slash_command("info", "Gets info about a tag, or a members tags.")
async def tag_info_slash_command(
    ctx: tanjun.abc.Context,
    name: t.Optional[str],
    member: t.Optional[hikari.InteractionMember]
) -> None:
    """Gets info about a tag, or a members tags."""
    assert isinstance(ctx.client, SlashClient)

    if (not name and not member):
        await ctx.respond(
            ctx.client.errors.embed(ctx, "Please pass a tag name or member to get tag information about.")
        )

    elif name and member:
        await ctx.respond(
            ctx.client.errors.embed(ctx, "You can only get info on a tag name OR a member, but not both.")
        )

    elif name:
        query = "SELECT TagOwner, Uses FROM tags WHERE TagName = $1 AND GuildID = $2;"

        if not (tag_name_info := await ctx.client.bot.pool.row(query, name.lower(), ctx.guild_id)):
            await ctx.respond(
                ctx.client.errors.embed(ctx, f"No `{name}` tag exists.")
            )
            return None

        await ctx.respond(
            ctx.client.embeds.build(
                ctx=ctx,
                title=f"{ctx.client.bot.yes} Tag information",
                footer="BYPASS",
                description=f"Requested tag: `{name}`""",
                fields=[
                    ("Owner", f"<@!{tag_name_info[0]}>", True),
                    ("Uses", tag_name_info[1], True),
                ]
            )
        )

    elif member:
        query = "SELECT TagName, Uses FROM tags WHERE TagOwner = $1 AND GuildID = $2;"

        if not (tag_member_info := await ctx.client.bot.pool.rows(query, member.id, ctx.guild_id)):
            await ctx.respond(
                ctx.client.errors.embed(ctx, f"{member.mention} hasn't created any tags yet. Boo!")
            )
            return None

        assert tag_member_info is not None
        fields = [
            ("Name", "\n".join(t[0] for t in tag_member_info), True),
            ("Uses", "\n".join(str(t[1]) for t in tag_member_info), True),
        ]

        await ctx.respond(
            ctx.client.embeds.build(
                ctx=ctx,
                title=f"{ctx.client.bot.yes} Tag information",
                footer="BYPASS",
                description=f"Requested member: {member.mention}",
                fields=fields,
            )
        )


@tag_group.with_command
@tanjun.as_slash_command("list", "List this guilds tags.")
async def tag_list__slash_command(ctx: tanjun.abc.Context) -> None:
    """Command for listing all tags."""
    assert isinstance(ctx.client, SlashClient)
    query = "SELECT TagName FROM tags WHERE GuildID = $1;"
    tags = await ctx.client.bot.pool.column(query, ctx.guild_id)

    # If there are no tags stored
    if not len(tags):
        await ctx.respond(
            ctx.client.errors.embed(ctx, "No tags for this guild yet, make one!")
        )
        return None

    assert ctx.guild_id is not None
    description: str = "\n".join(str(t) for t in tags)

    await ctx.respond(
        ctx.client.embeds.build(
            ctx=ctx,
            footer="BYPASS",
            title=f"{ctx.client.bot.yes} Tags for {(await ctx.client.rest.fetch_guild(ctx.guild_id)).name}",
            description=f"```{description}```",
        )
    )


@tag_group.with_command
@tanjun.with_str_slash_option("content", "The content of the tag.")
@tanjun.with_str_slash_option("name", "The name of the tag to create.")
@tanjun.as_slash_command("create", "Create a new tag.")
async def tag_create_slash_command(ctx: tanjun.abc.Context, name: str, content: str) -> None:
    """Command for creating a new tag."""
    assert isinstance(ctx.client, SlashClient)

    # Can't create a reserved tag
    if (name := name.lower()) in RESERVED_TAGS:
        await ctx.respond(
            ctx.client.errors.embed(
                ctx, f"That tag name is reserved. All of these are: ```{', '.join(RESERVED_TAGS)}```"
            )
        )

    # If someone tries to make an already made tag... yeah thats a use :kek:
    elif owner := await ctx.client.bot.pool.fetch(
        "UPDATE tags SET Uses = Uses + 1 WHERE GuildID = $1 AND TagName = $2 RETURNING TagOwner;",
        ctx.guild_id, name
    ):
        await ctx.respond(
            ctx.client.errors.embed(
                ctx, f"Sorry, `{name}` was already created by <@!{owner}>. Try a different tag name.",
            )
        )
        return None

    # A successful tag creation
    await ctx.client.bot.pool.execute(
        "INSERT INTO tags (guildid, tagowner, tagname, tagcontent) VALUES ($1, $2, $3, $4);",
        ctx.guild_id, ctx.author.id, name, content
    )

    await ctx.respond(
        ctx.client.embeds.build(
            ctx=ctx,
            footer="BYPASS",
            description=f"{ctx.client.bot.yes} `{name}` tag created by {ctx.author.mention}.",
        )
    )


@tag_group.with_command
@tanjun.with_str_slash_option("content", "The content of the tag.")
@tanjun.with_str_slash_option("name", "The name of the tag to edit.")
@tanjun.as_slash_command("edit", "Edit an existing tag you own.")
async def tag_edit_slash_command(ctx: tanjun.abc.Context, name: str, content: str) -> None:
    """Command for editing a tag you own."""
    name = name.lower()
    assert isinstance(ctx.client, SlashClient)

    if owner := await ctx.client.bot.pool.fetch(
        "SELECT TagOwner FROM tags WHERE GuildID = $1 AND TagName = $2;",
        ctx.guild_id, name
    ):
        # A successful tag edit
        if owner == ctx.author.id:
            await ctx.client.bot.pool.execute(
                "UPDATE tags SET TagContent = $1 WHERE TagName = $2 AND GuildID = $3;",
                content, name, ctx.guild_id
            )
            await ctx.respond(
                ctx.client.embeds.build(
                    ctx=ctx,
                    footer="BYPASS",
                    description=f"{ctx.client.bot.yes} `{name}` tag edited by {ctx.author.mention}.",
                )
            )
            return None

        # Author doesn't own the tag
        await ctx.respond(
            ctx.client.errors.embed(ctx, f"<@!{owner}> owns the `{name}` tag, you cannot edit it.")
        )
        return None

    # There is no tag with that name, do they want to make one?
    await ctx.respond(
        ctx.client.errors.embed(
            ctx,
            f"**WARNING**\nNo `{name}` tag exists to edit. Would you like to create it now?"
        )
    )

    # Checks the user and channel for validity
    def predicate(e: hikari.GuildMessageCreateEvent) -> bool:
        condition: bool = e.author_id == ctx.author.id and ctx.channel_id == e.channel_id
        return condition

    async with ctx.client.bot.stream(hikari.GuildMessageCreateEvent, 30) as stream:
        async for event in stream.filter(predicate):
            if event.content.startswith("y" or "Y"):
                await event.message.delete()
                await ctx.client.bot.pool.execute(
                    "INSERT INTO tags (GuildID, TagOwner, TagName, TagContent) "
                    "VALUES ($1, $2, $3, $4);",
                    ctx.guild_id, ctx.author.id, name, content
                )
                await ctx.edit_last_response(
                    embed=ctx.client.embeds.build(
                        ctx=ctx,
                        footer="BYPASS",
                        description=(
                            f"{ctx.client.bot.yes} `{name}` tag created by {ctx.author.mention}."
                        )
                    )
                )
                return

            elif event.content.startswith("n" or "N"):
                await event.message.delete()
                await ctx.edit_last_response(embed=ctx.client.errors.embed(ctx, f"Not creating new tag `{name}`"))
                return

    await ctx.edit_initial_response(
        embed=ctx.client.errors.embed(ctx, f"No `{name}` tag exists to edit.")
    )


@tag_group.with_command
@tanjun.with_member_slash_option("member", "The member to transfer the tag to.")
@tanjun.with_str_slash_option("name", "The name of the tag to transfer.")
@tanjun.as_slash_command("transfer", "Transfer a tag you own to another member.")
async def tag_transfer_slash_command(ctx: tanjun.abc.Context, name: str, member: hikari.InteractionMember) -> None:
    """Command for transferring a tag you own to someone else."""
    name = name.lower()
    assert isinstance(ctx.client, SlashClient)

    if owner := await ctx.client.bot.pool.fetch(
        "SELECT TagOwner FROM tags WHERE GuildID = $1 AND TagName = $2;", ctx.guild_id, name,
    ):
        # A successful transfer
        if owner == ctx.author.id:
            await ctx.client.bot.pool.execute(
                "UPDATE tags SET TagOwner = $1 WHERE GuildID = $2 AND TagName = $3;",
                member.id, ctx.guild_id, name
            )
            await ctx.respond(
                ctx.client.embeds.build(
                    ctx=ctx,
                    footer="BYPASS",
                    description=(
                        f"{ctx.client.bot.yes} `{name}` tag transferred "
                        f"from {ctx.author.mention} to {member.mention}."
                    )
                )
            )
            return None

        # Can't transfer a tag they don't own
        await ctx.respond(
            ctx.client.errors.embed(ctx, f"<@!{owner}> owns the `{name}` tag, you cannot transfer it.")
        )
        return None

    # Can't transfer a tag that doesn't exist
    await ctx.respond(
        ctx.client.errors.embed(ctx, f"No `{name}` tag exists to transfer.")
    )


@tag_group.with_command
@tanjun.with_str_slash_option("name", "The name of the tag to delete.")
@tanjun.as_slash_command("delete", "Delete a tag you own.")
async def tag_delete_slash_command(ctx: tanjun.abc.Context, name: str) -> None:
    """Command for deleting a tag you own."""
    name = name.lower()
    assert isinstance(ctx.client, SlashClient)

    if owner := await ctx.client.bot.pool.fetch(
        "SELECT TagOwner FROM tags WHERE GuildID = $1 AND TagName = $2;", ctx.guild_id, name
    ):
        # A successful deletion
        if owner == ctx.author.id:
            await ctx.client.bot.pool.execute(
                "DELETE FROM tags WHERE GuildID = $1 AND TagName = $2;", ctx.guild_id, name
            )
            await ctx.respond(
                ctx.client.embeds.build(
                    ctx=ctx,
                    footer="BYPASS",
                    description=f"{ctx.client.bot.yes} `{name}` tag deleted by {ctx.author.mention}.",
                )
            )
            return None

        # Can't delete a tag they don't own
        await ctx.respond(
            ctx.client.errors.embed(ctx, f"<@!{owner}> owns the `{name}` tag, you cannot delete it.")
        )
        return None

    # Can't delete a tag that doesn't exist
    await ctx.respond(
        ctx.client.errors.embed(ctx, f"No `{name}` tag exists to delete.")
    )


@tanjun.as_loader
def load_component(client: tanjun.abc.Client) -> None:
    client.add_component(component.copy())
