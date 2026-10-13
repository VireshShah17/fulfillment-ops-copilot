import os
from retrieval.chunking import Chunk
from retrieval.vector_store import VectorStore


def test_vector_store_add_and_search():
    # Temporary mock storage path configuration
    test_db = ".cache/test_vector_store.json"

    if os.path.exists(test_db):
        os.remove(test_db)

    store = VectorStore(storage_path = test_db)

    # Prepare chunks data simulation
    chunk1 = Chunk(chunk_id = "doc1", text = "FedEx priority shipping rules", metadata = {"source": "fedex.md"})
    chunk2 = Chunk(chunk_id = "doc2", text = "UPS standard delivery matrix exceptions", metadata = {"source": "ups.md"})

    # Exact 3-dimension space vectors representation setup mock
    store.add_documents([chunk1, chunk2], [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])

    # Query matching vector space closest to chunk1 vector pattern direction
    query_vector = [0.9, 0.1, 0.0]
    results = store.similarity_search(query_vector, top_k=1)

    assert len(results) == 1
    assert results[0].chunk_id == "doc1"
    assert results[0].score > 0.8

    # Clean up test artifact after evaluation
    if os.path.exists(test_db):
        os.remove(test_db)
