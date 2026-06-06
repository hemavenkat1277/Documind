import re

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

TOKEN_RE = re.compile(r"\S+")


def count_tokens(text):
    return len(TOKEN_RE.findall(text))

def build_text_splitter(chunk_size: int = 900, overlap: int = 160) -> RecursiveCharacterTextSplitter:
    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    return RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        length_function=count_tokens,
        separators=["\n\n", "\n", ". ", " ", ""],
    )

def chunk_documents(
        text:str,
        chunk_size: int =900,
        overlap: int =160,
        metadata: dict|None = None,
)->list[dict]:
    normalized = re.sub(r"\s+", " ",text).strip()
    if not normalized:
        return []
    
    source_document=Document(page_content=normalized,metadata=metadata or {})
    splitter=build_text_splitter(chunk_size,overlap)
    return splitter.split_documents([source_document])

def chunk_text(text:str,chunk_size:int =900,overlap:int=160)->list[str]:
    return [
        document.page_content
        for document in chunk_documents(text,chunk_size=chunk_size,overlap=overlap)
    ]
