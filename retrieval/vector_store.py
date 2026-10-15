import os
import json
import numpy as np
from typing import List, Dict, Any
from pydantic import BaseModel, Field
from retrieval.chunking import Chunk
from rank_bm25 import BM25Okapi


class SearchResult(BaseModel):
    """
        Structured response return format for similarity searches.
    """
    chunk_id: str
    text: str
    score: float
    metadata: Dict[str, Any] = Field(default_factory=dict)

class VectorStore:
    def __init__(self, storage_path: str = ".cache/vector_store.json"):
        self.storage_path = storage_path
        os.makedirs(os.path.dirname(self.storage_path), exist_ok = True)
        self.chunks: Dict[str, Dict[str, Any]] = {}
        self.embeddings: Dict[str, List[float]] = {}
        
        # Sparse Index State
        self.bm25_corpus = [] 
        self.chunk_ids_list = [] 
        self.bm25_index = None
        
        self._load_store()
        self._build_bm25()


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


    def _tokenize(self, text: str) -> List[str]:
        # Lightweight tokenization for BM25
        return text.lower().replace('\n', ' ').split()


    def _build_bm25(self):
        if not self.chunks:
            return
        
        self.chunk_ids_list = list(self.chunks.keys())
        self.bm25_corpus = [self._tokenize(self.chunks[cid]["text"]) for cid in self.chunk_ids_list]
        self.bm25_index = BM25Okapi(self.bm25_corpus)


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
        self._build_bm25() # Rebuild index when data is added


    def dense_search(self, query_embedding: List[float], top_k: int = 10) -> List[SearchResult]:
        if not self.embeddings:
            return []
            
        chunk_ids = list(self.embeddings.keys())
        matrix = np.array([self.embeddings[cid] for cid in chunk_ids])
        q_vec = np.array(query_embedding)

        dot_product = np.dot(matrix, q_vec)
        norms = np.linalg.norm(matrix, axis=1) * np.linalg.norm(q_vec)
        norms[norms == 0] = 1e-9
        scores = dot_product / norms

        top_indices = np.argsort(scores)[::-1][:top_k]

        return [
            SearchResult(
                chunk_id = chunk_ids[idx],
                text = self.chunks[chunk_ids[idx]]["text"],
                score = float(scores[idx]),
                metadata = self.chunks[chunk_ids[idx]]["metadata"]
            ) for idx in top_indices
        ]


    def sparse_search(self, query: str, top_k: int = 10) -> List[SearchResult]:

        if not self.bm25_index:
            return []
            
        tokenized_query = self._tokenize(query)
        scores = self.bm25_index.get_scores(tokenized_query)
        top_indices = np.argsort(scores)[::-1][:top_k]
        
        return [
            SearchResult(
                chunk_id = self.chunk_ids_list[idx],
                text = self.chunks[self.chunk_ids_list[idx]]["text"],
                score = float(scores[idx]),
                metadata = self.chunks[self.chunk_ids_list[idx]]["metadata"]
            ) for idx in top_indices if scores[idx] > 0
        ]


    def hybrid_search(self, query: str, query_embedding: List[float], top_k: int = 3, rrf_k: int = 60) -> List[SearchResult]:
        # Pull larger pools to fuse
        dense_results = self.dense_search(query_embedding, top_k = 10)
        sparse_results = self.sparse_search(query, top_k = 10)

        rrf_scores = {}
        
        # Calculate Reciprocal Rank Fusion for Dense
        for rank, res in enumerate(dense_results):
            rrf_scores[res.chunk_id] = rrf_scores.get(res.chunk_id, 0.0) + (1.0 / (rrf_k + rank + 1))
            
        # Calculate Reciprocal Rank Fusion for Sparse
        for rank, res in enumerate(sparse_results):
            rrf_scores[res.chunk_id] = rrf_scores.get(res.chunk_id, 0.0) + (1.0 / (rrf_k + rank + 1))
        
        # Sort by combined RRF score descending
        sorted_chunks = sorted(rrf_scores.items(), key = lambda x: x[1], reverse = True)[:top_k]
        
        return [
            SearchResult(
                chunk_id = cid,
                text = self.chunks[cid]["text"],
                score = score,
                metadata = self.chunks[cid]["metadata"]
            ) for cid, score in sorted_chunks
        ]
