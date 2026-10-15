from langchain_core.tools import tool
from retrieval.client import GeminiClient
from retrieval.vector_store import VectorStore
from mcp_server.server import (
    get_order_status as mcp_get_order_status,
    get_inventory_levels as mcp_get_inventory_levels,
    get_shipment_tracking as mcp_get_shipment_tracking
)


@tool
def search_knowledge_base(query: str) -> str:
    """
        Searches the RAG vector store for relevant context based on the user's query.
        Returns a combined string of the top 3 most relevant context chunks.
    """
    # Instantiate the client and store
    client = GeminiClient()
    store = VectorStore()
    # Generate the dense embedding for the query
    # embed_text expects a list of strings, so we wrap the query in a list
    # and extract the first (and only) embedding from the result
    query_embedding = client.embed_text([query])[0]
    
    # Perform a hybrid search to get the top 3 results
    results = store.hybrid_search(
        query = query, 
        query_embedding = query_embedding, 
        top_k = 3
    )
    
    # Extract the 'text' field from each SearchResult and join them
    texts = [res.text for res in results]
    
    # Return a clean, combined string for the LLM to process
    return "\n\n---\n\n".join(texts)


@tool
def get_order_status(order_id: str) -> str:
    """
        Returns the status, carrier, and shipping address for a given order.
    """

    return mcp_get_order_status(order_id)


@tool
def get_inventory_levels(sku: str) -> str:
    """
        Returns total on hand, allocated, and safety stock for a given SKU.
    """
    
    return mcp_get_inventory_levels(sku)


@tool
def get_shipment_tracking(tracking_number: str) -> str:
    """
        Returns current status, location, and exception codes for a tracking number.
    """
    
    return mcp_get_shipment_tracking(tracking_number)
