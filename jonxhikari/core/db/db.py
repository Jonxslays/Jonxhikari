import asyncio
import os
import typing as t

import asyncpg
import aiofiles

from jonxhikari import Config


class AsyncPGDatabase:
    """Wrapper class for AsyncPG Database access."""
    def __init__(self) -> None:
        self.calls = 0
        self.db = Config.env("PG_DB")
        self.host = Config.env("PG_HOST")
        self.user = Config.env("PG_USER")
        self.password = Config.env("PG_PASS")
        self.port = Config.env("PG_PORT", int)
        self.schema = "./jonxhikari/data/static/build.sql"

    async def connect(self) -> None:
        """""Opens a connection pool."""
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

    def lock(func: t.Callable[..., t.Any]) -> t.Callable[..., t.Any]: # type: ignore
        """A decorator for all database pool acquisitions.

        Args:
            func (t.Callable[..., t.Any]): The function we are wrapping.

        Returns:
            t.Callable[..., t.Any]: The same function but wrapped
                with a connection.
        """
        async def wrapper(self: "AsyncPGDatabase", *args: t.Any) -> t.Any:
            """A wrapper function that injects the acquired connection.

            Args:
                self (AsyncPGDatabase): The database instance.
                *args: (t.Any): The remaining args to pass to the
                    wrapped function.

            Returns:
                t.Any: The output of the wrapped function.
            """
            async with self.pool.acquire() as conn:
                self.calls += 1
                return await func(self, *args, conn=conn)

        return wrapper

    @lock
    async def fetch(self, q: str, *values: t.Any, conn: asyncpg.Connection) -> t.Optional[t.Any]:
        """Read 1 field of applicable data.

        Args:
            q (str): The query to execute.
            *values (t.Any): The values to pass to the sql query.

        Returns:
            t.Optional[t.Any]: The requested data or None if not found.
        """
        query = await conn.prepare(q)
        return await query.fetchval(*values)

    @lock
    async def row(self, q: str, *values: t.Any, conn: asyncpg.Connection) -> t.Optional[t.List[t.Any]]:
        """Read 1 row of applicable data.

        Args:
            q (str): The query to execute.
            *values (t.Any): The values to pass to the sql query.

        Returns:
            t.Optional[t.List[t.Any]]: A list containing the requested
                data or None if not found.
        """
        query = await conn.prepare(q)
        if data := await query.fetchrow(*values):
            return [r for r in data]

        return None

    @lock
    async def rows(self, q: str, *values: t.Any, conn: asyncpg.Connection) -> t.Optional[t.List[t.Iterable[t.Any]]]:
        """Read all rows of applicable data.

        Args:
            q (str): The query to execute.
            *values (t.Any): The values to pass to the sql query.

        Returns:
            t.Optional[t.List[t.Iterable[t.Any]]]: A list of tuples
                containing the requested data or None if not found.
        """
        query = await conn.prepare(q)
        if data := await query.fetch(*values):
            return [*map(lambda r: tuple(r.values()), data)]

        return None

    @lock
    async def column(self, q: str, *values: t.Any, conn: asyncpg.Connection) -> t.List[t.Any]:
        """Read a single column of applicable data.

        Args:
            q (str): The query to execute.
            *values (t.Any): The values to pass to the sql query.

        Returns:
            t.List[t.Any]: [description]
        """
        query = await conn.prepare(q)
        return [r[0] for r in await query.fetch(*values)]

    @lock
    async def execute(self, q: str, *values: t.Any, conn: asyncpg.Connection) -> None:
        """Execute a write operation on the database.

        Args:
            q (str): The query to execute.
            *values (t.Any): The values to pass to the sql query.
        """
        query = await conn.prepare(q)
        await query.fetch(*values)

    @lock
    async def executemany(self, q: str, values: t.List[t.Iterable[t.Any]], conn: asyncpg.Connection) -> None:
        """Execute a write operation for each set of values.

        Args:
            q (str): [description]
            values (t.List[t.Iterable[t.Any]]): A list of tuples
                containing the values to pass to the sql query.
        """
        query = await conn.prepare(q)
        await query.executemany(values)

    @lock
    async def scriptexec(self, path: str, conn: asyncpg.Connection) -> None:
        """Executes an sql script at a given path.

        Args:
            path (str): The path to the .sql file.
        """
        async with aiofiles.open(path, "r", encoding="utf-8") as script:
            await conn.execute((await script.read()))
