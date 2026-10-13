import os
import json
import numpy as np
from typing import List, Dict, Any
from pydantic import BaseModel, Field
from retrieval.chunking import Chunk


class SearchResult(BaseModel):
    """
        Structured response return format for similarity searches.
    """
    chunk_id: str
    text: str
    score: float
    metadata: Dict[str, Any] = Field(default_factory=dict)


class VectorStore:
    """
        Lightweight in-memory vector store persisting data on-disk as JSON.
    """
    def __init__(self, storage_path: str = ".cache/vector_store.json"):
        self.storage_path = storage_path
        # Ensure the directory tree wrapper exists safely
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        self.chunks: Dict[str, Dict[str, Any]] = {}
        self.embeddings: Dict[str, List[float]] = {}
        self._load_store()


    def _load_store(self):
        """
            Loads data matrix snapshots from disk if available.
        """
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r', encoding = 'utf-8') as f:
                    data = json.load(f)
                    self.chunks = data.get("chunks", {})
                    self.embeddings = data.get("embeddings", {})
            except Exception:
                self.chunks = {}
                self.embeddings = {}


    def _save_store(self):
        """
            Persists tracking updates locally on-disk.
        """
        with open(self.storage_path, 'w', encoding = 'utf-8') as f:
            json.dump({"chunks": self.chunks, "embeddings": self.embeddings}, f, indent = 2)


    def add_documents(self, chunks: List[Chunk], embeddings: List[List[float]]):
        """
            Appends new structured fragments and vectors mapping data points into store.
        """
        if len(chunks) != len(embeddings):
            raise ValueError("Chunks count must exactly match embeddings matrix dimensions.")

        for chunk, embedding in zip(chunks, embeddings):
            self.chunks[chunk.chunk_id] = {
                "chunk_id": chunk.chunk_id,
                "text": chunk.text,
                "metadata": chunk.metadata
            }
            self.embeddings[chunk.chunk_id] = embedding

        self._save_store()


    def similarity_search(self, query_embedding: List[float], top_k: int = 3) -> List[SearchResult]:
        """
            Performs cosine math operations to extract top matched context paths.
        """
        if not self.embeddings:
            return []

        # Convert mappings safely into high-speed numpy data frames
        chunk_ids = list(self.embeddings.keys())
        matrix = np.array([self.embeddings[cid] for cid in chunk_ids])
        q_vec = np.array(query_embedding)

        # Vectorized Cosine Similarity Math Execution
        dot_product = np.dot(matrix, q_vec)
        matrix_norms = np.linalg.norm(matrix, axis=1)
        q_norm = np.linalg.norm(q_vec)

        # Zero division error prevention buffer edge-case
        norms = matrix_norms * q_norm
        norms[norms == 0] = 1e-9
        
        scores = dot_product / norms

        # Get top matching indices sorted in descending order
        top_indices = np.argsort(scores)[::-1][:top_k]

        results = []
        for idx in top_indices:
            cid = chunk_ids[idx]
            chunk_data = self.chunks[cid]
            results.append(SearchResult(
                chunk_id = cid,
                text = chunk_data["text"],
                score = float(scores[idx]),
                metadata = chunk_data["metadata"]
            ))

        return results
