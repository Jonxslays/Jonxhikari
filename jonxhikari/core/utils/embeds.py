import datetime

import hikari


class Embeds:
    """Embed constructor class

    functions:
         - build: Constructs the embed.
    """

    def build(self, **kwargs) -> hikari.Embed:
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

        self.fields = kwargs.get("fields")
        self._ctx = kwargs.get("ctx")
        self.title = kwargs.get("title")
        self.desc = kwargs.get("description")
        self.footer = kwargs.get("footer")
        self.header = kwargs.get("header")
        self.header_icon = kwargs.get("header_icon")
        self.thumbnail = kwargs.get("thumbnail")
        self.image = kwargs.get("image")
        self.color = kwargs.get("color")
        self.time = datetime.datetime.now().astimezone()

        self._prime()
        self._plus_fields()
        self._extras()

        return self.embed

    def _prime(self) -> None:
        """Generates inital embed."""
        self.embed = hikari.Embed(
            title = self.title,
            description = self.desc,
            timestamp = self.time,
            color = self.color or hikari.Color.from_hex_code("#713dc7")
        )

    def _plus_fields(self) -> None:
        """Adds fields to the embed"""
        for name, value, inline in self.fields:
            self.embed.add_field(name=name, value=value, inline=inline)

    def _extras(self) -> None:
        """Adds finals elements to the embed."""
        self.embed.set_thumbnail(self.thumbnail or self._ctx.bot.me.avatar_url)

        self.embed.set_author(
            name = self.header or "Jonxhikari",
            icon = self.header_icon
        )

        self.embed.set_footer(
            text = self.footer or f"Invoked by: {self._ctx.author.username}",
            icon = self._ctx.author.avatar_url or self._ctx.bot.me.avatar_url
        )

        self.embed.set_image(self.image)
