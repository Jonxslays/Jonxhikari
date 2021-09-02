from .config import Config
from .core import Errors
from .core import Embeds
from .core import Lines
from .core import Database
from .core import SlashClient
from .core import Bot

__version__ = "0.6.0"

__all__ = [
    "Bot",
    "Config",
    "SlashClient",
    "Errors",
    "Embeds",
    "Lines",
    "Database",
]
