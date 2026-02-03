# ask questions and get answer from your content using RAG

import json
import os
import argparse
from pathlib import Path

from dotenv import load_dotenv
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS, Chroma
from langchain_core.documents import Document

from utils.dial_client import DIALClient

load_dotenv()


class BasicRAG:
    """loads chunks, search them and generate answer via DIAL"""

    def __init__(
        self,
        vector_store_type: str = "faiss",
        embedding_model_name: str = "all-MiniLM-L6-v2",
        content_dir: str = "data/extracted_content",
    ):
        """setup client and embeddings, vector store built later"""
        self.dial_client = DIALClient()
        self.vector_store_type = vector_store_type
        self.embeddings = HuggingFaceEmbeddings(model_name=embedding_model_name)
        self.vector_store = None
        self.content_dir = content_dir

    def load_documents(self, content_dir: str = "data/extracted_content"):
        """read chunks.json and turn into Document list"""
        path = Path(content_dir) / "chunks.json"
        if not path.exists():
            raise FileNotFoundError(
                f"No chunks found at {path}. Run extract_content.py --url <URL> first."
            )
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        if not data:
            return []
        documents = []
        for item in data:
            content = item.get("content", "")
            metadata = item.get("metadata", {})
            documents.append(Document(page_content=content, metadata=metadata))
        return documents

    def create_vector_store(self, documents: list):
        """build faiss or chroma index from documents"""
        if not documents:
            return
        if self.vector_store_type == "faiss":
            self.vector_store = FAISS.from_documents(documents, self.embeddings)
        elif self.vector_store_type == "chromadb":
            self.vector_store = Chroma.from_documents(
                documents, self.embeddings, collection_name="basic_rag"
            )
        else:
            raise ValueError(f"Unknown vector_store_type: {self.vector_store_type}")

    def retrieve_relevant_docs(self, query: str, k: int = 3):
        """find top k chunks that match the query"""
        if self.vector_store is None:
            raise RuntimeError("Vector store not built. Call load_documents() and create_vector_store() first.")
        return self.vector_store.similarity_search(query, k=k)

    def generate_response(self, query: str, retrieved_docs: list) -> str:
        """send context + question to DIAL and return the answer"""
        context = "\n\n".join(doc.page_content for doc in retrieved_docs)
        prompt = (
            "Use the following context to answer the question. "
            "If the context does not contain the answer, say so.\n\n"
            f"Context:\n{context}\n\nQuestion: {query}"
        )
        messages = [{"role": "user", "content": prompt}]
        return self.dial_client.get_completion(messages)

    def query(self, query: str) -> str:
        """full pipeline: load if needed, retrieve, then generate"""
        if self.vector_store is None:
            documents = self.load_documents(self.content_dir)
            if not documents:
                return "No documents found in data/extracted_content. Run extract_content.py --url <URL> first."
            self.create_vector_store(documents)
        retrieved = self.retrieve_relevant_docs(query, k=3)
        return self.generate_response(query, retrieved)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Basic RAG Question Answering")
    parser.add_argument("--query", required=True, help="Query to ask")
    parser.add_argument(
        "--vector-store",
        default="faiss",
        choices=["faiss", "chromadb"],
        help="Vector store type",
    )
    parser.add_argument(
        "--content-dir",
        default="data/extracted_content",
        help="Directory containing chunks.json",
    )

    args = parser.parse_args()

    if not os.getenv("DIAL_API_KEY") or os.getenv("DIAL_API_KEY") == "<YOUR_API_KEY_HERE>":
        print("Error: Set DIAL_API_KEY in .env to use the RAG pipeline.")
        raise SystemExit(1)

    rag = BasicRAG(
        vector_store_type=args.vector_store,
        content_dir=args.content_dir,
    )
    try:
        answer = rag.query(args.query)
        print(answer)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        raise SystemExit(1)
    except Exception as e:
        print(f"Error: {e}")
        raise SystemExit(1)
