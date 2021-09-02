from __future__ import annotations
import os
import sqlite3
import typing as t

import lightbulb
from aiosqlite import connect
from apscheduler.triggers.cron import CronTrigger


class Database:
    def __init__(self, bot: lightbulb.Bot) -> None:
        self.bot = bot
        self._calls = 0
        self.path = f"{bot._dynamic}/database.db3"
        self.build_path = f"{bot._static}/build.sql"
        self.bot.scheduler.add_job(self.commit, CronTrigger(second=0))

    async def connect(self) -> None:
        if not os.path.isdir(self.bot._dynamic):
            # If cloned, this dir likely won't exist, so make it.
            os.makedirs(self.bot._dynamic)

        self.cxn = await connect(self.path)
        await self.execute("pragma journal_mode=wal")
        await self.executescript(self.build_path)
        await self.commit()

    async def commit(self) -> None:
        await self.cxn.commit()

    async def close(self) -> None:
        await self.commit()
        await self.cxn.close()

    async def sync(self) -> None:
        await self.commit()

    async def field(self, command: str, *values: object) -> t.Any:
        cur = await self.cxn.execute(command, tuple(values))
        self._calls += 1

        if (row := await cur.fetchone()) is not None:
            return row[0] if row[0] else None

        return None

    async def record(self, command: str, *values: object) -> t.Any:
        cur = await self.cxn.execute(command, tuple(values))
        self._calls += 1

        return await cur.fetchone()

    async def records(self, command: str, *values: object) -> t.Iterable[t.Any]:
        cur = await self.cxn.execute(command, tuple(values))
        self._calls += 1
        data = await cur.fetchall()

        return await cur.fetchall()

    async def column(self, command: str, *values: object) -> t.List[t.Union[str, int, None]]:
        cur = await self.cxn.execute(command, tuple(values))
        self._calls += 1

        return [row[0] for row in await cur.fetchall()]

    async def execute(self, command: str, *values: object) -> int:
        cur = await self.cxn.execute(command, tuple(values))
        self._calls += 1

        return cur.rowcount

    async def executemany(self, command: str, valueset: tuple[str, t.Any]) -> int:
        cur = await self.cxn.executemany(command, valueset)
        self._calls += 1

        return cur.rowcount

    async def executescript(self, path: str, **kwargs: dict[str, t.Any]) -> None:
        with open(path, "r", encoding="utf-8") as script:
            await self.cxn.executescript(script.read().format(**kwargs))

        self._calls += 1
