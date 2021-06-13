import lightbulb
import hikari


class Tags(lightbulb.Plugin):
    def __init__(self, bot: lightbulb.Bot) -> None:
        self.bot = bot
        self.reserved = (
            "create", "delete", "info", "transfer", "edit"
        )
        super().__init__()

    @lightbulb.group(name="tag")
    async def tag_cmd(self, ctx: lightbulb.Context, name: str) -> None:
        """Command group for managing guild specific tags."""
        print("main tag command was called.")

    @tag_cmd.command(name="create")
    async def tag_create_cmd(self, ctx: lightbulb.Context, name: str, *, content: str) -> None:
        """Command for creating a new tag."""
        print("subcommand create called")

    @tag_cmd.command(name="edit")
    async def tag_edit_cmd(self, ctx: lightbulb.Context, name: str, *, content: str) -> None:
        """Command for editing a tag you own."""
        print("subcommand edit called")

    @tag_cmd.command(name="transfer")
    async def tag_transfer_cmd(self, ctx: lightbulb.Context, name: str, member: hikari.Member) -> None:
        """Command for transferring a tag you own to someone else."""
        print("subcommand transfer called")

    @tag_cmd.command(name="delete")
    async def tag_delete_cmd(self, ctx: lightbulb.Context, name: str) -> None:
        """Command for deleting a tag."""
        print("subcommand delete called")


def load(bot: lightbulb.Bot) -> None:
    bot.add_plugin(Tags(bot))


def unload(bot: lightbulb.Bot) -> None:
    bot.remove_plugin("Tags")
