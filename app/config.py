from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "DocuMind"
    database_url: str = "postgresql://documind:documind@localhost:5432/documind"
    kafka_bootstrap_servers: str = "localhost:9092"
    redis_url: str = "redis://localhost:6379/0"
    upload_dir: Path = Path("storage/uploads")

    embedding_dim: int = Field(default=384, ge=64)
    emdbeddin_model_name: str = "BAAI/bge-small-en-v1.5"
    embedding_device: str = "cpu"
    normalize_embeddings: bool = True
    chunk_size: int = Field(default=900, ge=200)
    chunk_overlap: int = Field(default=160, ge=0)
    retrieval_top_k: int = Field(default=8, ge=1)
    rerank_top_k: int = Field(default=4, ge=1)
    cache_ttl_seconds: int = Field(default=300, ge=0)


@lru_cache
def get_settings() -> Settings:
    return Settings()

