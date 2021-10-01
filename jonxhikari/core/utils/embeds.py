import datetime
import typing as t

import lightbulb
import hikari
import tanjun


FieldsT = t.Optional[list[tuple[t.Union[str, int], t.Union[str, int], bool]]]
CtxT = t.Union[lightbulb.Context, tanjun.abc.Context]
ResourceishT = t.Optional[hikari.files.Resourceish]


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
        self.fields: FieldsT = kwargs.get("fields")
        self._ctx: CtxT = kwargs.get("ctx")
        self.title: t.Optional[str] = kwargs.get("title")
        self.desc: t.Optional[str] = kwargs.get("description")
        self.footer: t.Optional[str] = kwargs.get("footer")
        self.header: t.Optional[str] = kwargs.get("header")
        self.header_url: t.Optional[str] = kwargs.get("header_url")
        self.header_icon: ResourceishT = kwargs.get("header_icon")
        self.thumbnail: ResourceishT = kwargs.get("thumbnail")
        self.image: ResourceishT = kwargs.get("image")
        self.color: t.Optional[hikari.colors.Colorish] = kwargs.get("color")
        self.time: datetime.datetime = kwargs.get(
            "timestamp", datetime.datetime.now().astimezone()
        )

        assert self._ctx is not None  # You happy now mypy???

        embed = (
            hikari.Embed(
                title=self.title,
                description=self.desc,
                timestamp=self.time,
                color=self.color or hikari.Color.from_hex_code("#713dc7"),
            )
            .set_thumbnail(self.thumbnail)
            .set_image(self.image)
            .set_author(name=self.header, url=self.header_url, icon=self.header_icon)
            .set_footer(
                text=(
                    None
                    if self.footer == "BYPASS"
                    else (self.footer or f"Invoked by: {self._ctx.author.username}")
                ),
                icon=(
                    None
                    if self.footer == "BYPASS"
                    else (
                        self._ctx.author.avatar_url
                        or (
                            self._ctx.bot.get_me().avatar_url
                            if isinstance(self._ctx, lightbulb.Context)
                            else self._ctx.client.bot.get_me().avatar_url
                        )
                    )
                ),
            )
        )

        if self.fields:
            for name, value, inline in self.fields:
                embed.add_field(name=name, value=value, inline=inline)

        return embed
