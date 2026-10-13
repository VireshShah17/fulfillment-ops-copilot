import time
import pytest
from unittest.mock import MagicMock, patch
from google.genai import errors
from retrieval.client import GeminiClient, api_cache


@pytest.fixture(autouse = True)
def clear_test_cache():
    """
        Clears the cache before running the test cases.
    """
    api_cache.clear()
    yield
    api_cache.clear()


@patch('retrieval.client.genai.Client')
def test_gemini_client_smoke_test(mock_genai_class):
    """
        Task 0.5 Smoke Test:
        1. First call mock standard roundtrip hit karegi.
        2. Second call diskcache se < 10ms me result degi.
        3. Embed text mock karke dimension metrics verify karegi.
    """
    # 1. Mocking setup for generate_content
    mock_client_instance = MagicMock()
    mock_genai_class.return_value = mock_client_instance
    
    mock_text_response = MagicMock()
    mock_text_response.text = "PONG"
    mock_client_instance.models.generate_content.return_value = mock_text_response

    # 2. Mocking setup for embed_content (text-embedding-004 vector space dimension)
    mock_embed_response = MagicMock()
    mock_embedding_obj = MagicMock()
    # 768 elements array simulation for text-embedding-004
    mock_embedding_obj.values = [0.1] * 768  
    mock_embed_response.embeddings = [mock_embedding_obj]
    mock_client_instance.models.embed_content.return_value = mock_embed_response

    # Environment setup & Init client
    with patch.dict('os.environ', {'GEMINI_API_KEY': 'mock_secret_key'}):
        client = GeminiClient()

        # --- CALL 1: First Network Request (Billable Hit Simulation) ---
        prompt = "Respond with 'PONG' only."
        first_start = time.perf_counter()
        res1 = client.generate_text(prompt)
        first_duration = (time.perf_counter() - first_start) * 1000

        assert res1 == "PONG"
        mock_client_instance.models.generate_content.assert_called_once()

        # --- CALL 2: Second Hit (Should return from diskcache < 10ms) ---
        second_start = time.perf_counter()
        res2 = client.generate_text(prompt)
        second_duration = (time.perf_counter() - second_start) * 1000

        assert res2 == "PONG"
        # Network call sirf ek hi baar call hona chahiye tha, dusri baar nahi
        mock_client_instance.models.generate_content.assert_called_once() 
        
        print(f"\n[Cache Timing Profile] First Call: {first_duration:.2f}ms, Cached Second Call: {second_duration:.2f}ms")
        assert second_duration < 10.0, f"Cache call took too long: {second_duration:.2f}ms"

        # --- CALL 3: Vector Array Mapping & Dimension Mapping Assertion ---
        embeddings = client.embed_text(["Warehouse bin A-12"])
        
        assert len(embeddings) == 1
        assert len(embeddings[0]) == 768, f"Expected 768 dimensions, got {len(embeddings[0])}"
        mock_client_instance.models.embed_content.assert_called_once()
