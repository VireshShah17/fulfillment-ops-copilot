import json
import os
import sys
import logging

# Set runtime path lookup manually
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from retrieval.vector_store import VectorStore
from retrieval.client import GeminiClient


# Setup lightweight logs
logging.basicConfig(level = logging.INFO)
logger = logging.getLogger("Harness Evaluation")


def load_golden_set():
    with open("evals/datasets/golden_set.json", "r", encoding = "utf-8") as f:
        return json.load(f)


def calculate_metrics(results, target_doc, k = 3):
    hit = 0
    mrr = 0.0
    for rank, res in enumerate(results[:k]):

        if res.metadata.get("source") == target_doc:
            hit = 1
            mrr = 1.0 / (rank + 1)
            break

    return hit, mrr


def run_evals():
    golden_set = load_golden_set()
    store = VectorStore()
    client = GeminiClient()

    metrics = {
        "dense": {"hits": 0, "mrr": 0.0},
        "sparse": {"hits": 0, "mrr": 0.0},
        "hybrid": {"hits": 0, "mrr": 0.0}
    }

    total = len(golden_set)
    logging.info(f"Running Ablation Evaluation on {total} queries...\n")

    for item in golden_set:
        query = item["query"]
        target_doc = item["target_doc"]
        # 1. Fetch cached embedding
        query_emb = client.embed_text([query])[0]
        # 2. Execute parallel search methods
        dense_res = store.dense_search(query_emb, top_k = 3)
        sparse_res = store.sparse_search(query, top_k = 3)
        hybrid_res = store.hybrid_search(query, query_emb, top_k = 3)

        # 3. Score the hits and MRR
        for mode, res in [("dense", dense_res), ("sparse", sparse_res), ("hybrid", hybrid_res)]:
            hit, mrr = calculate_metrics(res, target_doc, k = 3)
            metrics[mode]["hits"] += hit
            metrics[mode]["mrr"] += mrr

    # 4. Print ablation table
    logging.info("| Method | Recall@3 | MRR |")
    logging.info("|---|---|---|")
    
    hybrid_avg_mrr = 0.0
    
    for mode in ["dense", "sparse", "hybrid"]:
        recall = (metrics[mode]["hits"] / total) * 100
        avg_mrr = metrics[mode]["mrr"] / total
        
        if mode == "hybrid":
            hybrid_avg_mrr = avg_mrr
            
        logging.info(f"| {mode.capitalize()} | {recall:.1f}% | {avg_mrr:.3f} |")

    # 5. Eval Gate Logic
    if hybrid_avg_mrr < 0.90:
        logger.error(f"Evaluation Failed: Hybrid MRR {hybrid_avg_mrr:.3f} is below the 0.90 threshold.")
        sys.exit(1)
    else:
        logger.info(f"Evaluation Passed: Hybrid MRR {hybrid_avg_mrr:.3f} meets or exceeds the 0.90 threshold.")
        sys.exit(0)


if __name__ == "__main__":
    run_evals()
