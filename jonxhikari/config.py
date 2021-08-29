import logging
import typing as t
from logging.handlers import TimedRotatingFileHandler
from os import environ

import dotenv


dotenv.load_dotenv()


class DatabaseLoggingFilter(logging.Filter):
    """Filters out Database sync logs."""
    def filter(self, record: logging.LogRecord) -> bool:
        return (
            'Running job "Database.commit' not in (m := record.getMessage())
            and 'Job "Database.commit' not in m
        )

class Config:
    """Object related to configuration."""

    @staticmethod
    def env(var: str, type_: type = str) -> t.Any:
        """Gets environment variables from a `.env` file."""
        try:
            return type_(environ[var])

        except KeyError:
            raise LookupError(f"`{var}` is not defined in config.") from None

        except ValueError:
            raise LookupError(f"Can't convert `{var}` to `{type_}`.")

    @staticmethod
    def logging() -> logging.Logger:
        """Logs to a file that rotates every 3 days"""
        log = logging.getLogger("root")
        log.setLevel(logging.INFO)

        trfh = TimedRotatingFileHandler(
            "./jonxhikari/data/logs/main.log",
            when="D", interval=3, encoding="utf-8",
            backupCount=10
        )

        ff = logging.Formatter(
            f"[%(asctime)s] %(levelname)s ||| %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        trfh.setFormatter(ff)
        trfh.addFilter(DatabaseLoggingFilter())
        log.addHandler(trfh)

        return log
