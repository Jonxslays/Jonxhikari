from __future__ import annotations
from os import environ

import dotenv


dotenv.load_dotenv()


class Config:
    """Gets environment variables from a `.env` file."""
    @classmethod
    def get(cls, var: str) -> str | int | bool:
        try:
            t, v = environ[var].split(":", maxsplit=1)

            if t == "str":
                return str(v)

            if t == "int":
                return int(v)

            if t == "bool":
                _v = {
                    "True": True,
                    "true": True,
                    "False": False,
                    "false": False,
                }

                if v not in _v.keys():
                    raise LookupError(
                        f"`{var}` is using an invalid boolean value in config."
                    )

                return _v[v]

        except KeyError:
            raise LookupError(f"`{var}` is not defined in config.") from None

        raise LookupError(f"`{var}` has an invalid type in config.")
