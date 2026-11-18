from work02.corpus import Document, chunk_documents


def test_chunk_overlap():
    doc = Document("d1", "t", "a" * 1000)
    chunks = chunk_documents([doc], chunk_size=400, overlap=50)
    assert len(chunks) >= 2
    assert chunks[0].char_start == 0