import pytest
import os
from unittest.mock import MagicMock, patch
from retrieval.chunking import chunk_all_documents
from retrieval.client import GeminiClient
from retrieval.vector_store import VectorStore

def test_baseline_retrieval_pipeline_integrity():
    # 1. Clear physical temporary file footprint safely beforehand
    test_db = ".cache/test_retrieval_store.json"
    if os.path.exists(test_db):
        os.remove(test_db)
        
    # 2. Extract configuration data input chunk paths
    chunks = chunk_all_documents("data/docs")
    assert len(chunks) >= 1, "No document chunks loaded from data/docs."
    
    with patch.dict('os.environ', {'GEMINI_API_KEY': 'mock_pipeline_testing_secret_key'}):
        with patch('retrieval.client.genai.Client') as mock_genai_class:
            client = GeminiClient()
            
            # Initialize clean instance setup
            store = VectorStore(storage_path=test_db)
            
            # CRITICAL FIX: Flush any implicitly loaded global state tracking data fields
            store.chunks = {}
            store.embeddings = {}
            
            # 3. Generate structured dynamic mock mappings vectors matrices
            embeddings = []
            for chunk in chunks:
                if chunk.metadata.get("source") == "carrier_exceptions_fedex_ups.md":
                    # Vector pointing purely in the 1st dimension
                    embeddings.append([1.0] + [0.0] * 767)
                else:
                    # Vector pointing purely in the 2nd dimension (orthogonal)
                    embeddings.append([0.0, 1.0] + [0.0] * 766)
            
            # Add filtered elements directly into vector store wrapper map tracking matrix
            store.add_documents(chunks, embeddings)
            
            # 4. Fire target math validation query structure assertion block
            query_vector = [1.0] + [0.0] * 767
            top_matches = store.similarity_search(query_vector, top_k=1)
            
            assert len(top_matches) == 1, "VectorStore similarity search mapping lookup failed."
            assert top_matches[0].metadata["source"] == "carrier_exceptions_fedex_ups.md", \
                f"Failing mapping match. Received unexpected priority document index: {top_matches[0].metadata['source']}"

    # Clean up tracking instance outputs after successful verification execution pipeline
    if os.path.exists(test_db):
        os.remove(test_db)

