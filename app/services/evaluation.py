from uuid import uuid4

from psycopg import AsyncConnection

async def record_retrieval_event(
    conn:AsyncConnection,
    question: str,
    answer: str,
    latency_ms: int,
    top_score: float| None,
    cache_hit: bool,
)-> None:
    await conn.execute(
        """
        INSERT INTO retrieval_events
            (id,question,answer,latency_ms,top_score,cache_hit,answer_length)
            VALUES
            (%s,%s,%s,%s,%s,%s,%s)
        """,
        (uuid4(),question,answer,latency_ms,top_score,cache_hit,len(answer)),
    )

async def recent_retrieval_metrics(conn:AsyncConnection, limit:int=25)->list[dict]:
    rows = await conn.execute(
        """
        select id,question,latency_ms,top_score,cache_hit,answer_length,created_at
        FROM retrieval_events
        ORDER BY created_at DESC
        LIMIT %s
        """,
        (limit,),
    )
    return await rows.fetchall()