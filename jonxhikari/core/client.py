import typing as t
from pathlib import Path

import hikari
import tanjun


class SlashClient(tanjun.Client):
    """Client for handling Slash Commands."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def load_modules(self):
        """Loads Tanjun modules."""
        return super().load_modules(
            *(f"jonxhikari.core.modules.{p.stem}" for p in Path(".").glob("./jonxhikari/core/modules/*.py"))
        )
