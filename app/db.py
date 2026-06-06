from pathlib import Path
from typing import AsyncIterator 

from psycopg import AsyncConnection 
from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool

from app.config import Settings,get_settings

_pool: AsyncConnectionPool | None = None

def _scheme_sql() -> str:
    return Path(__file__).with_name("sql").joinpath("schema.sql").read_text()


async def open_pool(settings:Settings|None=None)->AsyncConnectionPool:
    global pool
    if _pool is None:
        resolved=settings or get_settings()
        _pool=AsyncConnectionPool(
            conninfo=resolved.database_url,
            kwargs={"row_factory": dict_row},
            min_size=1,
            max_size=10,
            open=False,
        )
        await _pool.open()
    return _pool

async def close_pool()->None:
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool=None

async def init_db(settings:Settings|None=None)->None:
    pool=await open_pool(settings)
    async with pool.connection() as conn:
        await conn.execute(_scheme_sql())

async def get_db()->AsyncIterator[AsyncConnection]:
    pool=await open_pool()
    async with pool.connection() as conn:
        yield conn