import os
import logging
import hashlib
import json
from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from google import genai
from google.genai import errors
from tenacity import retry, stop_after_attempt, wait_random_exponential, retry_if_exception_type
from diskcache import Cache


# Setup lightweight logs
logging.basicConfig(level = logging.INFO)
logger = logging.getLogger("GeminiClient")

# Setup a local, lightweight disk cache in the .cache folder (keeps RAM footprint near 0)
cache_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".cache", "gemini_cache")
api_cache = Cache(cache_dir)


class GeminiSettings(BaseSettings):
    """
        Safely loads and validates configuration using Pydantic Settings.
    """
    api_key: str = Field(alias = "GEMINI_API_KEY")
    model: str = Field(default = "gemini-2.5-flash", alias = "GEMINI_MODEL")
    embedding_model: str = Field(default = "text-embedding-004", alias = "GEMINI_EMBEDDING_MODEL")

    model_config = SettingsConfigDict(
        env_file = ".env",
        env_file_encoding = "utf-8",
        extra = "ignore"
    )

class GeminiClient:
    """
        Resilient wrapper around the official Google GenAI SDK.
    """
    def __init__(self):
        # Validate configurations
        self.settings = GeminiSettings()
        # Initialize the official Google GenAI client
        self.client = genai.Client(api_key = self.settings.api_key)
        logger.info("GeminiClient initialized successfully with validated configs.")
        logger.info(f"Gemini Model {self.settings.model} and Embedding model {self.settings.embedding_model}")


    @retry(
        reraise = True,
        stop = stop_after_attempt(4),
        wait = wait_random_exponential(multiplier = 1, min = 2, max = 10),
        retry = retry_if_exception_type((errors.APIError, ConnectionError))
    )
    def _execute_generate_text(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        """
            Internal text generation executor wrapped with exponential backoff + jitter retries.
        """
        logger.info(f"Dispatching API call for text generation using model: {self.settings.model}")
        
        config = {}
        if system_instruction:
            config["system_instruction"] = system_instruction

        response = self.client.models.generate_content(
            model = self.settings.model,
            contents = prompt,
            config = config if config else None
        )

        return response.text


    def generate_text(self, prompt: str, system_instruction: Optional[str] = None) -> str:
        """
            Exposes text generation with local disk caching to prevent duplicate billable hits.
        """
        cache_key = f"text:{prompt}:{system_instruction or ''}"
        
        cached_res = api_cache.get(cache_key)
        
        if cached_res is not None:
            logger.info("Cache hit: Returning stored text generation data from disk.")
            return cached_res

        # Call the resilient internal method
        result = self._execute_generate_text(prompt, system_instruction)
        api_cache.set(cache_key, result, expire = 86400) # Cached for 24 hours
        
        return result


    @retry(
        reraise = True,
        stop = stop_after_attempt(4),
        wait = wait_random_exponential(multiplier = 1, min = 2, max = 10),
        retry = retry_if_exception_type((errors.APIError, ConnectionError))
    )
    def _execute_single_embed(self, text: str) -> List[float]:
        """
            Internal single-text embedding executor wrapped with tenacity retry logic.
        """
        response = self.client.models.embed_content(
            model = self.settings.embedding_model,
            contents = text
        )
        return response.embeddings[0].values

    
    def embed_text(self, texts: List[str]) -> List[List[float]]:
        """
            Exposes vector embeddings generations backed by an efficient per-chunk on-disk caching layer.
        """
        results = []
        for text in texts:
            # Create a deterministic lookup key for this specific text chunk
            raw_embed = f"{self.settings.embedding_model}:{text}"
            cache_key = f"embed:{hashlib.sha256(raw_embed.encode()).hexdigest()}"
            
            cached_res = api_cache.get(cache_key)
            
            if cached_res is not None:
                results.append(cached_res)
            else:
                logger.info(f"Cache miss: Embedding new chunk via API...")
                vector = self._execute_single_embed(text)
                api_cache.set(cache_key, vector, expire = 86400) # Cached for 24 hours
                results.append(vector)
                
        return results
