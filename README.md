# 📦 Fulfillment Ops Copilot

**An Agentic RAG System for Warehouse Exception Handling & Operations**

The Fulfillment Ops Copilot is an enterprise-grade AI agent designed to help warehouse staff and customer service representatives instantly resolve order delays, track shipments, and query standard operating procedures (SOPs). 

Instead of relying on a simple chatbot, this system uses a **LangGraph state machine** to dynamically route user queries. It can intelligently decide whether to query a live relational database for order statuses, search an unstructured vector database for operational policies, or combine both to synthesize a complete resolution for complex fulfillment exceptions.

## 🏗️ Architecture

```text
                             +-----------------------+
                             |   Client / Frontend   |
                             |   (FastAPI Stream)    |
                             +-----------+-----------+
                                         |
                                         v
                         +-------------------------------+
                         |   LangGraph Supervisor/Router |
                         |   (Gemini 3.1 Pro / Guard)  |
                         +---------------+---------------+
                                         |
            +----------------------------+----------------------------+
            | (Docs Query)                                            | (DB Lookup)
            v                                                         v
+-----------------------+                                 +-----------------------+
|  Retrieval Pipeline   |                                 |   FastMCP Server      |
|  - BM25 (Sparse)      |                                 |   (Read-Only SQL)     |
|  - Gemini Emb (Dense) |                                 +-----------+-----------+
|  - RRF Fusion         |                                             |
+-----------+-----------+                                 +-----------------------+
            |                                             |  SQLite Database      |
            | SOPs/Carrier Runbooks                       |  (Orders/Inventory)   |
            +----------------------------+----------------+-----------------------+
                                         |
                                         v
                             [Final Streamed Response]
```

## ✨ Key Features & Engineering Decisions

*   **Hybrid Search & Reciprocal Rank Fusion (RRF):** Pure vector search fails at exact string matching (like SKUs or Order IDs). This system implements a hybrid pipeline, querying a Dense vector index (Cosine Similarity) and a Sparse keyword index (BM25) in parallel, normalizing and merging the scores via RRF to achieve a perfect 1.0 Mean Reciprocal Rank (MRR).
*   **Model Context Protocol (MCP) Integration:** LLMs should not have direct, raw access to databases. Live transactional data (Orders, Inventory, Shipments) is exposed to the agent via a standalone, read-only `FastMCP` server using strictly parameterized SQL queries to eliminate prompt injection vulnerabilities.
*   **Memory-Optimized Caching:** Designed to run on constrained hardware (4 GB RAM), the system uses a persistent, deterministic disk-backed caching layer (`diskcache`) combined with exponential backoff (`tenacity`) to minimize LLM/Embedding API roundtrips, reduce latency to <10ms, and protect against rate limits.
*   **CI/CD Evaluation Gate:** AI infrastructure rots without probabilistic testing. The project includes a custom evaluation harness that runs a "Golden Set" of queries against the retrieval engine. If an upstream code change degrades the Hybrid MRR below 0.90, the CI script automatically fails the build.
*   **Security Guardrails:** A pre-agent routing node inspects all incoming requests, instantly rejecting malicious prompt injections or out-of-scope queries (e.g., "Write a poem") before burning billable LLM tokens.

## 📊 Evaluation & Ablation Study

To prove the efficacy of the Hybrid Search pipeline over a standard RAG setup, an ablation study was conducted against a Golden Set of 10 complex warehouse operational queries. 

| Method | Recall@3 | MRR |
|---|---|---|
| Dense (Vectors Only) | 100.0% | 0.950 |
| Sparse (BM25 Only) | 100.0% | 0.883 |
| **Hybrid (Dense + Sparse + RRF)** | **100.0%** | **1.000** |

*Result: Hybrid search successfully placed the exact target document at Rank 1 for every single query.*

## 🚀 Quick Start

### 1. Prerequisites
*   Python 3.11 or 3.12
*   Google Gemini API Key (AI Studio)

### 2. Installation
Clone the repository and install the minimal dependency stack:
```bash
git clone https://github.com/yourusername/fulfillment-ops-copilot.git
cd fulfillment-ops-copilot
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Environment Setup
Create a `.env` file in the root directory:
```env
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-3.1-pro-preview
GEMINI_EMBEDDING_MODEL=gemini-embedding-2
```

### 4. Initialize Data & Vectors
Generate the SQLite database seed data and embed the Markdown SOPs:
```bash
python scripts/setup_db.py
python scripts/index_docs.py
```

## 🛠️ Usage

### Option A: Run the Interactive CLI Agent
Test the cognitive engine directly in your terminal, complete with token-usage telemetry:
```bash
python scripts/run_agent.py
```
*Try asking: "Why is order ORD-1042 delayed, what is the policy for this exception, and what should I do?"*

### Option B: Run the FastAPI Server
Serve the agent via a production-ready asynchronous REST endpoint:
```bash
uvicorn app.main:app --reload
```
Test the endpoint in a new terminal:
```bash
curl -X POST "http://127.0.0.1:8000/chat" \
     -H "Content-Type: application/json" \
     -d '{"query": "Status of ORD-5001"}'
```

### Option C: Run the CI/CD Evaluation Gate
Verify the mathematical integrity of the retrieval pipeline and graph logic:
```bash
chmod +x scripts/ci.sh
./scripts/ci.sh
```

## 📁 Repository Structure

*   `agents/`: LangGraph state machine, tool definitions, and system prompts.
*   `app/`: FastAPI application layer and Pydantic schemas.
*   `data/`: Synthetic operational Markdown docs and SQL seed scripts.
*   `evals/`: Golden dataset and the evaluation harness for CI gating.
*   `mcp_server/`: Standalone Model Context Protocol server exposing read-only database tools.
*   `retrieval/`: Structure-aware Markdown chunking, Gemini API clients, and the Hybrid Vector Store.
*   `scripts/`: Database initialization, indexing, and CLI execution scripts.
*   `tests/`: Deterministic unit tests for graph routing and API resilience.