import os
import sys
import logging

# Set runtime path lookup manually
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from retrieval.chunking import chunk_all_documents
from retrieval.client import GeminiClient
from retrieval.vector_store import VectorStore

logging.basicConfig(level = logging.INFO)
logger = logging.getLogger("IndexScript")


def main():
    logger.info("Starting documentation ingestion engine pipeline...")
    
    # 1. Parse all documentation folders
    chunks = chunk_all_documents("data/docs")
    
    if not chunks:
        logger.warning("No markdown/text document chunks found in data/docs/. Exiting.")
        return
        
    logger.info(f"Successfully processed and generated {len(chunks)} structural fragments.")

    # 2. Extract texts array layer for batch embedding extraction
    texts = [chunk.text for chunk in chunks]

    # 3. Request vectors mapped array generation via GeminiClient
    logger.info("Dispatching batch embedding request matrix map layers...")
    client = GeminiClient()
    embeddings = client.embed_text(texts)

    # 4. Ingest compilation blocks safely inside local Vector Store
    store = VectorStore()
    store.add_documents(chunks, embeddings)
    logger.info("Successfully persisted vector mappings database snapshot into local storage disk.")


if __name__ == "__main__":
    main()
