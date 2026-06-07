from functools import lru_cache

from langchain_huggingface import HuggingFaceEmbeddings
from app.config import get_settings

@lru_cache
def get_embedding_model() ->HuggingFaceEmbeddings:
    settings = get_settings()
    return HuggingFaceEmbeddings(
        model_name=settings.embedding_model_name,
        model_kwargs={"device":settings.embedding_device},
        encode_kwargs={"normalize_embeddings":settings.normalize_embeddings},
    )


def embed_text(text:str)->list[float]:
    return get_embedding_model().embed_query(text)

def embed_many(texts : list[str])->list[list[float]]:
    return get_embedding_model().embed_documents(texts)

def vector_to_pg(vector: list[float]) -> str:
    return "["+",".join(f"{value:.6f}" for value in vector)+"]"
