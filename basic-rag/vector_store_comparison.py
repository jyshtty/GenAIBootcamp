# compare faiss vs chroma - indexing time, query speed and storage

import os
import time
import tempfile
import shutil
from pathlib import Path
from typing import List, Dict, Any

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS, Chroma
from langchain_core.documents import Document


# fallback docs when theres no chunks.json yet
SAMPLE_DOCUMENTS = [
    "Machine learning is a subset of artificial intelligence that enables systems to learn from data.",
    "Neural networks consist of layers of nodes that process inputs and produce outputs.",
    "Natural language processing deals with understanding and generating human language.",
    "Embeddings are dense vector representations used for similarity and retrieval.",
    "Retrieval augmented generation combines retrieval with language models for grounded answers.",
    "Vector stores index embeddings for fast similarity search at scale.",
    "FAISS is a library for efficient similarity search and clustering of dense vectors.",
    "ChromaDB is an open-source embedding database designed for AI applications.",
    "Document chunking with overlap helps preserve context across boundaries.",
    "RAG pipelines typically retrieve top-k documents and pass them as context to an LLM.",
]


def get_doc_size(path: str) -> int:
    """size of file or folder in bytes"""
    p = Path(path)
    if not p.exists():
        return 0
    if p.is_file():
        return p.stat().st_size
    return sum(f.stat().st_size for f in p.rglob("*") if f.is_file())


class VectorStoreComparison:
    """run faiss vs chroma and print timings + storage"""

    def __init__(self, embedding_model_name: str = "all-MiniLM-L6-v2"):
        """one embedding model for both so its fair"""
        self.embeddings = HuggingFaceEmbeddings(model_name=embedding_model_name)
        self._faiss_store = None
        self._faiss_path = None
        self._chroma_path = None
        self._chromadb_store = None

    def _to_documents(self, documents: List[str]) -> List[Document]:
        """strings to LangChain docs"""
        return [Document(page_content=text, metadata={"source": f"doc_{i}"}) for i, text in enumerate(documents)]

    def setup_faiss_store(self, documents: List[str]):
        """build faiss index from docs"""
        if documents and isinstance(documents[0], Document):
            docs = documents
        else:
            docs = self._to_documents(documents)
        self._faiss_store = FAISS.from_documents(docs, self.embeddings)
        return self._faiss_store

    def setup_chromadb_store(self, documents: List[str], persist_directory: str = None):
        """build chroma index, optionally persist to folder"""
        if documents and isinstance(documents[0], Document):
            docs = documents
        else:
            docs = self._to_documents(documents)
        if persist_directory is None:
            persist_directory = tempfile.mkdtemp(prefix="chroma_compare_")
        self._chroma_path = persist_directory
        self._chromadb_store = Chroma.from_documents(
            docs, self.embeddings, persist_directory=persist_directory
        )
        return self._chromadb_store

    def measure_indexing_performance(self, documents: List[str]) -> Dict[str, float]:
        """time to build each index in seconds"""
        docs = self._to_documents(documents) if documents and isinstance(documents[0], str) else documents
        if not docs:
            docs = self._to_documents(SAMPLE_DOCUMENTS)

        start = time.perf_counter()
        self.setup_faiss_store(docs)
        faiss_time = time.perf_counter() - start

        chroma_dir = tempfile.mkdtemp(prefix="chroma_idx_")
        start = time.perf_counter()
        Chroma.from_documents(docs, self.embeddings, persist_directory=chroma_dir)
        chroma_time = time.perf_counter() - start
        if os.path.exists(chroma_dir):
            shutil.rmtree(chroma_dir, ignore_errors=True)

        return {"faiss": faiss_time, "chromadb": chroma_time}

    def measure_query_performance(
        self, query: str, num_queries: int = 100, faiss_store=None, chroma_store=None
    ) -> Dict[str, float]:
        """avg time per similarity_search for each store"""
        faiss_store = faiss_store or self._faiss_store
        chroma_store = chroma_store or self._chromadb_store
        results = {}

        if faiss_store:
            start = time.perf_counter()
            for _ in range(num_queries):
                faiss_store.similarity_search(query, k=3)
            results["faiss"] = (time.perf_counter() - start) / num_queries

        if chroma_store:
            start = time.perf_counter()
            for _ in range(num_queries):
                chroma_store.similarity_search(query, k=3)
            results["chromadb"] = (time.perf_counter() - start) / num_queries

        return results

    def compare_storage_requirements(
        self, faiss_save_dir: str = None, chroma_dir: str = None
    ) -> Dict[str, int]:
        """how many bytes each store use"""
        result = {}
        if faiss_save_dir and os.path.exists(faiss_save_dir):
            result["faiss"] = get_doc_size(faiss_save_dir)
        else:
            if self._faiss_store:
                tmp = tempfile.mkdtemp(prefix="faiss_size_")
                try:
                    self._faiss_store.save_local(tmp)
                    result["faiss"] = get_doc_size(tmp)
                finally:
                    shutil.rmtree(tmp, ignore_errors=True)
            else:
                result["faiss"] = 0

        if chroma_dir and os.path.exists(chroma_dir):
            result["chromadb"] = get_doc_size(chroma_dir)
        elif getattr(self, "_chroma_path", None) and os.path.exists(self._chroma_path):
            result["chromadb"] = get_doc_size(self._chroma_path)
        else:
            result["chromadb"] = 0

        return result

    def run_comparison(self):
        """do the full comparison and print report"""
        print("=== Vector Store Comparison Report ===\n")

        documents = SAMPLE_DOCUMENTS
        chunks_path = Path("data/extracted_content/chunks.json")
        if chunks_path.exists():
            try:
                import json
                with open(chunks_path, encoding="utf-8") as f:
                    data = json.load(f)
                documents = [item["content"] for item in data[:20]]
                print(f"Using {len(documents)} documents from {chunks_path}\n")
            except Exception:
                pass

        docs = self._to_documents(documents)

        print("Indexing performance (time to build index):")
        idx_times = self.measure_indexing_performance(documents)
        for store_name, t in idx_times.items():
            print(f"  {store_name}: {t:.3f}s")

        chroma_persist = tempfile.mkdtemp(prefix="chroma_compare_")
        try:
            self._chroma_path = chroma_persist
            self._chromadb_store = Chroma.from_documents(
                docs, self.embeddings, persist_directory=chroma_persist
            )

            query = "What is machine learning?"
            print(f"\nQuery performance (avg over 50 runs, query='{query[:40]}...'):")
            q_times = self.measure_query_performance(query, num_queries=50)
            for store_name, t in q_times.items():
                print(f"  {store_name}: {t*1000:.2f} ms per query")

            storage = self.compare_storage_requirements(chroma_dir=chroma_persist)
            print("\nStorage (bytes):")
            for store_name, size in storage.items():
                print(f"  {store_name}: {size} bytes ({size/1024:.1f} KB)")
        finally:
            if os.path.exists(chroma_persist):
                shutil.rmtree(chroma_persist, ignore_errors=True)

        print("\n--- Recommendation ---")
        print("  FAISS: Faster indexing and query; in-memory or save/load from disk. Best for single-node, large batches.")
        print("  ChromaDB: Persistent by default; good for multi-session apps and when you need metadata filtering.")


if __name__ == "__main__":
    comparison = VectorStoreComparison()
    comparison.run_comparison()
