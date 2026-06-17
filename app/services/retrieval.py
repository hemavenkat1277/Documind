from psycopg import AsyncConnection

from app.config import get_settings
from app.services.embeddings import get_embedding_model,vector_to_pg
from app.services.reranker import get_reranker 

async def retrieve(
        conn:AsyncConnection,
        question:str,
        top_k:int|None=None,
) -> list[dict]:
    settings = get_settings()
    embedding_model=get_embedding_model()
    vector=vector_to_pg(embedding_model.embed_query(question))
    recall_limit = max(settings.retrivel_top_k, top_k or settings.rerank_top_k)*3

    rows = await conn.execute(
        """
        SELECT  
        c.document_id,
        d.file_name,
        c.chunk_index,
        c.content,
        1 - (c.embedding <=> %s::vector) as similarity
        from chunks c
        join documents d on d.id=c.document_id
        where c.embedding is not null
        order by c.embedding <=> %ss::vector
        limit %s
        """,
        (vector,vector,recall_limit)
    )
    candidates = await rows.fecthall()
    limit = top_k or settings.rerank_top_k

    return [
        {
            **item.candidate,
            "similarity":float(item.candidate["similarity"]),
            "rerank_score":item.rerank_score,
        }
        for item in get_reranker().rerank(question,candidates,limit=limit)
    ]