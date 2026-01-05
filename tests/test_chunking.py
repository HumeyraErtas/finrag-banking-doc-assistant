from app.chunking import chunk_pages

def test_chunk_pages_empty():
    pages = [(1, ""), (2, "   \n\n")]
    chunks = chunk_pages(pages)
    assert chunks == []

def test_chunk_pages_basic():
    pages = [(1, "Bu bir test metnidir. " * 200)]
    chunks = chunk_pages(pages, chunk_size=200, overlap=50)
    assert len(chunks) > 1
    assert chunks[0].page_start == 1
    assert chunks[0].page_end == 1
    assert chunks[0].text.strip() != ""
