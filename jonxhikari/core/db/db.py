import asyncio
import os
import sqlite3
import typing as t

import asyncpg
import aiofiles
import hikari
from aiosqlite import connect
from apscheduler.triggers.cron import CronTrigger

from jonxhikari import Config


class AsyncPGDatabase:
    def __init__(self) -> None:
        self.calls = 0
        self.db = Config.env("PG_DB")
        self.host = Config.env("PG_HOST")
        self.user = Config.env("PG_USER")
        self.password = Config.env("PG_PASS")
        self.port = Config.env("PG_PORT", int)
        self.schema = "./jonxhikari/data/static/build.sql"

    async def connect(self) -> None:
        """Opens a connection pool."""
        self.pool = await asyncpg.create_pool(
            user = self.user,
            host = self.host,
            port = self.port,
            database = self.db,
            password = self.password,
            loop = asyncio.get_running_loop(),
        )

        await self.scriptexec(self.schema)

    async def close(self) -> None:
        """Closes the connection pool."""
        await self.pool.close()
        print("Closed connection pool.")

    def lock(func: t.Callable[..., t.Any]) -> t.Callable[..., t.Any]: # type: ignore
        """Decorator for aquiring the pool."""
        async def wrapper(self: "AsyncPGDatabase", *args: t.Any) -> t.Any:
            async with self.pool.acquire() as conn:
                self.calls += 1
                return await func(self, *args, conn=conn)

        return wrapper

    @lock
    async def fetch(self, q: str, *values: t.Any, conn: asyncpg.Connection) -> t.Any:
        """Read 1 field of applicable data."""
        query = await conn.prepare(q)
        return await query.fetchval(*values)

    @lock
    async def row(self, q: str, *values: t.Any, conn: asyncpg.Connection) -> t.Optional[t.List[t.Any]]:
        """Read 1 row of applicable data."""
        query = await conn.prepare(q)
        if data := await query.fetchrow(*values):
            return [r for r in data]

        return None

    @lock
    async def rows(self, q: str, *values: t.Any, conn: asyncpg.Connection) -> t.Optional[t.List[t.Iterable[t.Any]]]:
        """Read all rows of applicable data."""
        query = await conn.prepare(q)
        if data := await query.fetch(*values):
            return [*map(lambda r: tuple(r.values()), data)]

        return None

    @lock
    async def column(self, q: str, *values: t.Any, conn: asyncpg.Connection) -> t.List[t.Any]:
        """Read a single column of applicable data."""
        query = await conn.prepare(q)
        return [r[0] for r in await query.fetch(*values)]

    @lock
    async def execute(self, q: str, *values: t.Any, conn: asyncpg.Connection) -> None:
        """Execute a write operation on the database."""
        query = await conn.prepare(q)
        await query.fetch(*values)

    @lock
    async def executemany(self, q: str, values: t.List[t.Iterable[t.Any]], conn: asyncpg.Connection) -> None:
        """Execute a write operation for each iterable in the list passed to values."""
        query = await conn.prepare(q)
        await query.executemany(values)

    @lock
    async def scriptexec(self, path: str, conn: asyncpg.Connection) -> None:
        """Executes a .sql script at a given path."""
        async with aiofiles.open(path, "r", encoding="utf-8") as script:
            await conn.execute((await script.read()))
