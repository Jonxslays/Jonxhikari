import datetime
import typing as t

import lightbulb
import hikari


class Embeds:
    """Embed constructor class."""

    def build(self, **kwargs: t.Any) -> hikari.Embed:
        """Builds an embed from given kwargs.

        kwargs:
             - ctx: required
             - title: optional
             - description: optional
             - fields: optional
             - footer: optional
             - header: optional
             - header_icon: optional
             - thumbnail: optional
             - image: optional
             - color: optional

        Returns:
             - hikari.Embed
        """
        self.fields: t.Optional[list[tuple[str, str, bool]]] = kwargs.get("fields")
        self._ctx: lightbulb.Context = kwargs.get("ctx")
        self.title: t.Optional[str] = kwargs.get("title")
        self.desc: t.Optional[str] = kwargs.get("description")
        self.footer: t.Optional[str] = kwargs.get("footer")
        self.header: t.Optional[str] = kwargs.get("header")
        self.header_icon: t.Any = kwargs.get("header_icon")
        self.thumbnail: t.Any = kwargs.get("thumbnail")
        self.image: t.Any = kwargs.get("image")
        self.color: t.Any = kwargs.get("color")
        self.time: datetime.datetime = datetime.datetime.now().astimezone()

        embed = hikari.Embed(
            title = self.title,
            description = self.desc,
            timestamp = self.time,
            color = self.color or hikari.Color.from_hex_code("#713dc7")
        ).set_thumbnail(
            self.thumbnail
        ).set_image(
            self.image
        ).set_author(
            name = self.header or "Jonxhikari",
            icon = self.header_icon
        ).set_footer(
            text = self.footer or f"Invoked by: {self._ctx.author.username}",
            icon = self._ctx.author.avatar_url or self._ctx.bot.me.avatar_url
        )

        if self.fields:
            for name, value, inline in self.fields:
                embed.add_field(name=name, value=value, inline=inline)

        return embed
