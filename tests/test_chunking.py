import pytest

from app.services.chunking import chunk_text

def test_chunk_test_uses_langchain_splitter()->None:
    text=" ".join(str(number) for number in range(10))

    chunks=chunk_text(text,chunk_size=4,overlap=1)

    assert len(chunks)>1
    assert chunks[0].startswith("0")
    assert chunks[-1].endswith("9")

# def test_chunk_text_rejects_bad_overlap()->None:
#     with pytest.raises(V)