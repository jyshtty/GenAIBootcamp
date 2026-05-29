"""
Compare FAISS vs ChromaDB vector stores.

Measures indexing time, query latency, and disk footprint, then prints
a recommendation based on the results.

Example usage:
    python vector_store_comparison.py
"""

import time
import os
import tempfile
from typing import List, Dict

from langchain_core.documents import Document
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS, Chroma

SAMPLE_TEXTS = [
    "Machine learning is a subset of artificial intelligence.",
    "Deep learning uses neural networks with many layers.",
    "Natural language processing helps computers understand text.",
    "Retrieval Augmented Generation combines search with language models.",
    "Vector databases store embeddings for semantic similarity search.",
    "FAISS is an efficient similarity search library developed by Meta.",
    "ChromaDB is an AI-native open-source embedding database.",
    "Embeddings are dense numerical representations of semantic meaning.",
    "Semantic search finds similar content based on meaning rather than keywords.",
    "LangChain is a framework for building LLM-powered applications.",
    "Transformers revolutionized natural language processing tasks.",
    "Attention mechanisms allow models to focus on relevant parts of input.",
    "Supervised learning uses labelled data to train predictive models.",
    "Unsupervised learning discovers hidden patterns without labels.",
    "Reinforcement learning trains agents through reward and penalty signals.",
    "Tokenization splits text into sub-word units for LLM processing.",
    "Fine-tuning adapts pre-trained models to specific downstream tasks.",
    "Prompt engineering crafts inputs to guide language model outputs.",
    "RAG reduces hallucination by grounding answers in retrieved facts.",
    "Vector similarity is often computed using cosine or dot-product distance.",
]


class VectorStoreComparison:
    def __init__(self, embedding_model: str = "all-MiniLM-L6-v2"):
        """Initialize with a shared embedding model to ensure fair comparison."""
        print(f"Loading embedding model '{embedding_model}'...")
        self.embeddings = HuggingFaceEmbeddings(
            model_name=embedding_model,
            model_kwargs={"device": "cpu"},
        )
        self.faiss_store = None
        self.chroma_store = None
        self._chroma_persist_dir = None

    @staticmethod
    def _make_documents(texts: List[str]) -> List[Document]:
        return [Document(page_content=t, metadata={"idx": i}) for i, t in enumerate(texts)]

    # ------------------------------------------------------------------
    # Store setup
    # ------------------------------------------------------------------

    def setup_faiss_store(self, documents: List[Document]):
        """Build an in-memory FAISS index."""
        self.faiss_store = FAISS.from_documents(documents, self.embeddings)
        return self.faiss_store

    def setup_chromadb_store(self, documents: List[Document]):
        """Build a ChromaDB collection in a temp directory."""
        self._chroma_persist_dir = tempfile.mkdtemp()
        self.chroma_store = Chroma.from_documents(
            documents,
            self.embeddings,
            collection_name="comparison",
            persist_directory=self._chroma_persist_dir,
        )
        return self.chroma_store

    # ------------------------------------------------------------------
    # Performance measurements
    # ------------------------------------------------------------------

    def measure_indexing_performance(self, documents: List[Document]) -> Dict[str, float]:
        """Time how long each store takes to build an index."""
        results = {}

        start = time.perf_counter()
        self.setup_faiss_store(documents)
        results["faiss_index_time_s"] = round(time.perf_counter() - start, 4)

        start = time.perf_counter()
        self.setup_chromadb_store(documents)
        results["chroma_index_time_s"] = round(time.perf_counter() - start, 4)

        return results

    def measure_query_performance(self, query: str, num_queries: int = 50) -> Dict[str, float]:
        """Average query latency over num_queries runs."""
        results = {}

        if self.faiss_store:
            start = time.perf_counter()
            for _ in range(num_queries):
                self.faiss_store.similarity_search(query, k=3)
            results["faiss_avg_query_ms"] = round(
                (time.perf_counter() - start) / num_queries * 1000, 4
            )

        if self.chroma_store:
            start = time.perf_counter()
            for _ in range(num_queries):
                self.chroma_store.similarity_search(query, k=3)
            results["chroma_avg_query_ms"] = round(
                (time.perf_counter() - start) / num_queries * 1000, 4
            )

        return results

    def compare_storage_requirements(self) -> Dict[str, str]:
        """Estimate disk usage for each store."""
        results = {}

        if self.faiss_store:
            with tempfile.TemporaryDirectory() as d:
                self.faiss_store.save_local(d)
                total = sum(
                    os.path.getsize(os.path.join(d, f)) for f in os.listdir(d)
                )
            results["faiss_disk_bytes"] = total
            results["faiss_disk_human"] = f"{total / 1024:.1f} KB"

        if self._chroma_persist_dir and os.path.exists(self._chroma_persist_dir):
            total = sum(
                os.path.getsize(os.path.join(dp, f))
                for dp, _, files in os.walk(self._chroma_persist_dir)
                for f in files
            )
            results["chroma_disk_bytes"] = total
            results["chroma_disk_human"] = f"{total / 1024:.1f} KB"

        return results

    # ------------------------------------------------------------------
    # Full comparison report
    # ------------------------------------------------------------------

    def run_comparison(self, texts: List[str] = None, query: str = "What is machine learning?"):
        """Run all benchmarks and print a formatted comparison report."""
        texts = texts or SAMPLE_TEXTS
        docs = self._make_documents(texts)

        print("\n" + "=" * 55)
        print("  Vector Store Comparison Report")
        print("=" * 55)
        print(f"  Documents : {len(texts)}")
        print(f"  Embeddings: all-MiniLM-L6-v2  (384-dim)")
        print(f"  Query     : \"{query}\"")
        print("=" * 55)

        print("\n[1] Indexing Performance")
        index_times = self.measure_indexing_performance(docs)
        for k, v in index_times.items():
            print(f"  {k:<30} {v} s")

        print("\n[2] Query Performance  (50 runs avg)")
        query_times = self.measure_query_performance(query)
        for k, v in query_times.items():
            print(f"  {k:<30} {v} ms")

        print("\n[3] Storage Requirements")
        storage = self.compare_storage_requirements()
        for k, v in storage.items():
            if not k.endswith("_bytes"):
                print(f"  {k:<30} {v}")

        print("\n[4] Recommendations")
        fi = index_times.get("faiss_index_time_s", 0)
        ci = index_times.get("chroma_index_time_s", 0)
        fq = query_times.get("faiss_avg_query_ms", 0)
        cq = query_times.get("chroma_avg_query_ms", 0)

        faster_idx = "FAISS" if fi <= ci else "ChromaDB"
        faster_qry = "FAISS" if fq <= cq else "ChromaDB"
        print(f"  Faster indexing : {faster_idx}")
        print(f"  Faster querying : {faster_qry}")
        print()
        print("  FAISS    — In-memory, blazing-fast for read-heavy workloads.")
        print("             Best when you can reload the index on startup.")
        print("  ChromaDB — Persistent by default, supports metadata filtering.")
        print("             Better for large datasets and production deployments.")
        print("=" * 55)


if __name__ == "__main__":
    comparison = VectorStoreComparison()
    comparison.run_comparison()
