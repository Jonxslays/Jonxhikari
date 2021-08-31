import asyncio

import hikari
import tanjun

from jonxhikari import SlashClient


# SlashCommand tags TODO
# - [x] tag list
# - [x] tag get
# - [x] tag create
# - [x] tag edit
# - [ ] tag transfer
# - [ ] tag delete
# - [ ] tag info


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
@tanjun. as_slash_command("get", "Gets a tag from the database.")
async def tag_get_slash_command(ctx: tanjun.abc.Context, name: str) -> None:
    """Gets a tag from the database."""
    query = "UPDATE tags SET Uses = Uses + 1 WHERE GuildID = ? AND TagName = ? RETURNING TagContent"

    if content := await ctx.client.bot.db.field(query, ctx.guild_id, name.lower()):
        await ctx.respond(content)
        return None

    await ctx.respond(f"`{name}` is not a valid tag.")


@tag_group.with_command
@tanjun.as_slash_command("list", "List this guilds tags.")
async def tag_list__slash_command(ctx: tanjun.abc.Context) -> None:
    """Command for listing all tags."""
    query = "SELECT TagName from tags WHERE GuildID = ?"

    # If there are no tags stored
    if len(tags := await ctx.client.bot.db.column(query, ctx.guild_id)) == 0:
        await ctx.respond("No tags for this guild yet, make one!")
        return None

    await ctx.respond(f"```{', '.join(t for t in tags)}```")


@tag_group.with_command
@tanjun.with_str_slash_option("content", "The content of the tag.")
@tanjun.with_str_slash_option("name", "The name of the tag to create.")
@tanjun.as_slash_command("create", "Create a new tag.")
async def tag_create_slash_command(ctx: tanjun.abc.Context, name: str, content: str) -> None:
    """Command for creating a new tag."""

    # Can't create a reserved tag
    if (name := name.lower()) in RESERVED_TAGS:
        await ctx.respond(f"That tag name is reserved. All of these are: ```{', '.join(RESERVED_TAGS)}```")
        return None

    # If someone tries to make an already made tag... yeah thats a use :kek:
    if owner := await ctx.client.bot.db.field(
        "UPDATE tags SET Uses = Uses + 1 WHERE GuildID = ? AND TagName = ? RETURNING TagOwner",
        ctx.guild_id, name
    ):
        await ctx.respond(
            f"Sorry, `{name}` was already created by {ctx.author.mention}. "
            "Try a different tag name."
        )
        return None

    # A successful tag creation
    await ctx.client.bot.db.execute(
        "INSERT INTO tags (GuildID, TagOwner, TagName, TagContent) VALUES (?, ?, ?, ?)",
        ctx.guild_id, ctx.author.id, name, content
    )
    await ctx.respond(f"**SUCCESS**\n`{name}` tag created by {ctx.author.mention}.")


@tag_group.with_command
@tanjun.with_str_slash_option("content", "The content of the tag.")
@tanjun.with_str_slash_option("name", "The name of the tag to edit.")
@tanjun.as_slash_command("edit", "Edit an existing tag you own.")
async def tag_edit_slash_command(ctx: tanjun.abc.Context, name: str, content: str) -> None:
    """Command for editing a tag you own."""
    name = name.lower()

    if owner := await ctx.client.bot.db.field(
        "SELECT TagOwner FROM tags WHERE GuildID = ? AND TagName = ?",
        ctx.guild_id, name
    ):
        # A successful tag edit
        if owner == ctx.author.id:
            await ctx.client.bot.db.execute(
                "UPDATE tags SET TagContent = ? WHERE TagName = ? AND GuildID = ?",
                content, name, ctx.guild_id
            )
            await ctx.respond(f"**SUCCESS**\n`{name}` tag edited by {ctx.author.mention}.")
            return None

        # Author doesn't own the tag
        await ctx.respond(
            f"**FAILURE**\n{ctx.author.mention} owns the `{name}` tag, not you."
        )
        return None

    # There is no tag with that name, do they want to make one?
    await ctx.respond(f"**WARNING**\nNo `{name}` tag exists to edit. Would you like to create it now?")

    # Checks the user for validity
    def predicate(e: hikari.GuildMessageCreateEvent) -> bool:
        print("in check")
        return e.author_id == ctx.author.id

    try:
        e = await ctx.client.bot.wait_for(hikari.GuildMessageCreateEvent, 30, predicate)

    except asyncio.TimeoutError:
        await ctx.edit_initial_response(content=f"**TIMEOUT FAILURE**.\nNo `{name}` tag exists to edit.")

    else:
        # They do want to make a new tag
        if e.content.startswith("y" or "Y"):
            await ctx.client.bot.db.execute(
                "INSERT INTO tags (GuildID, TagOwner, TagName, TagContent) VALUES (?, ?, ?, ?)",
                ctx.guild_id, ctx.author.id, name, content
            )
            await e.message.respond(
                content=f"**SUCCESS**\n`{name}` tag created by {ctx.author.mention}.",
                reply=True,
            )

        # They don't want to make a new tag
        else:
            await e.message.respond(
                content=f"**ABORTED**\nNot creating new tag `{name}`",
                reply=True
            )


@tanjun.as_loader
def load_component(client: tanjun.abc.Client) -> None:
    client.add_component(component.copy())
