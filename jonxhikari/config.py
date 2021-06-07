from __future__ import annotations
import typing as t
from os import environ
from pathlib import Path

import dotenv


dotenv.load_dotenv()


class SecretsMeta(type):

    def resolve_value(cls, value: str) -> t.Callable[..., t.Any] | t.Any:
        _map: dict[str, t.Callable[..., t.Any]] = {
            "bool": bool,
            "int": int,
            "float": float,
            "file": lambda x: Path(x).read_text().strip("\n"),
            "str": str,
            "set": lambda x: set([cls.resolve_value(e.strip()) for e in x.split(",")]),
        }

        return _map[(v := value.split(":", maxsplit=1))[0]](v[1])

    def resolve_key(cls, key: str) -> t.Callable[..., t.Any]:
        try:
            return cls.resolve_key(environ[key])
        except:
            return cls.resolve_value(key)

    def __getattr__(cls, name: str) -> t.Callable[..., t.Any]:
        try:
            return cls.resolve_key(name)
        except KeyError:
            raise AttributeError(f"{name} is not a key in config.") from None

    def __getitem__(cls, name: str) -> t.Callable[..., t.Any]:
        return cls.__getattr__(name)


class Secrets(metaclass=SecretsMeta):
    pass
