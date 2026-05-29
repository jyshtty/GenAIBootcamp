"""
Basic RAG system using FAISS or ChromaDB vector stores and the DIAL API.

Pipeline: extract content → embed → index → retrieve → generate

Example usage:
    python basic_rag.py --url https://en.wikipedia.org/wiki/Machine_learning \
                        --query "What is machine learning?"
    python basic_rag.py --query "What is supervised learning?" --vector-store chromadb
"""

import os
import json
import argparse
from dotenv import load_dotenv
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS, Chroma
from langchain_core.documents import Document
from utils.dial_client import DIALClient
from extract_content import extract_content_from_url, save_chunks

load_dotenv()

DEFAULT_EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")


class BasicRAG:
    def __init__(
        self,
        vector_store_type: str = "faiss",
        embedding_model: str = DEFAULT_EMBEDDING_MODEL,
        content_dir: str = "data/extracted_content",
    ):
        """
        Initialize RAG system.

        Args:
            vector_store_type (str): "faiss" or "chromadb"
            embedding_model (str): HuggingFace sentence-transformer model name
            content_dir (str): Default directory holding chunks.json
        """
        self.content_dir = content_dir
        self.dial_client = DIALClient()
        self.vector_store_type = vector_store_type
        self.embeddings = HuggingFaceEmbeddings(
            model_name=embedding_model,
            model_kwargs={"device": "cpu"},
        )
        self.vector_store = None
        print(f"BasicRAG initialized | store={vector_store_type} | embeddings={embedding_model}")

    def load_documents(self, content_dir: str = None):
        """
        Load documents from a single chunks.json file (JSON array of {content, metadata}).

        Args:
            content_dir (str): Directory containing chunks.json (defaults to self.content_dir)

        Returns:
            list: LangChain Document objects

        Raises:
            FileNotFoundError: if chunks.json is missing.
        """
        content_dir = content_dir or getattr(self, "content_dir", "data/extracted_content")
        chunks_path = os.path.join(content_dir, "chunks.json")
        if not os.path.exists(chunks_path):
            raise FileNotFoundError(f"chunks.json not found in '{content_dir}'. Run extract_content.py first.")

        with open(chunks_path, encoding="utf-8") as f:
            data = json.load(f)

        documents = [
            Document(page_content=item["content"], metadata=item.get("metadata", {}))
            for item in data
        ]
        print(f"Loaded {len(documents)} documents from '{chunks_path}'")
        return documents

    def create_vector_store(self, documents: list):
        """
        Build a FAISS or ChromaDB vector store from documents.

        Args:
            documents (list): LangChain Document objects to index
        """
        if not documents:
            raise ValueError("Cannot create vector store: no documents provided.")

        if self.vector_store_type == "faiss":
            self.vector_store = FAISS.from_documents(documents, self.embeddings)
            print(f"FAISS index created with {len(documents)} documents.")
        else:
            self.vector_store = Chroma.from_documents(
                documents,
                self.embeddings,
                collection_name="basic_rag",
            )
            print(f"ChromaDB collection created with {len(documents)} documents.")

    def retrieve_relevant_docs(self, query: str, k: int = 3):
        """
        Return the k most semantically similar documents.

        Args:
            query (str): User query
            k (int): Number of documents to retrieve

        Returns:
            list: Most relevant Document objects
        """
        if not self.vector_store:
            print("Vector store not initialized. Call create_vector_store() first.")
            return []
        return self.vector_store.similarity_search(query, k=k)

    def generate_response(self, query: str, retrieved_docs: list):
        """
        Build a prompt from retrieved context and call DIAL API.

        Args:
            query (str): User query
            retrieved_docs (list): Retrieved Document objects

        Returns:
            str: Generated answer
        """
        context = "\n\n---\n\n".join(doc.page_content for doc in retrieved_docs)
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a knowledgeable assistant. Answer the user's question using "
                    "ONLY the provided context. If the context does not contain enough "
                    "information, say so clearly. Be concise and accurate."
                ),
            },
            {
                "role": "user",
                "content": f"Context:\n{context}\n\nQuestion: {query}\n\nAnswer:",
            },
        ]
        return self.dial_client.get_completion(messages)

    def query(self, query: str, k: int = 3):
        """
        Full RAG pipeline: retrieve relevant docs then generate an answer.

        Args:
            query (str): User query
            k (int): Number of documents to retrieve

        Returns:
            str: Generated response
        """
        docs = self.retrieve_relevant_docs(query, k=k)
        if not docs:
            return "No relevant documents found. Please load content first."
        return self.generate_response(query, docs)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Basic RAG Question Answering")
    parser.add_argument("--query", required=True, help="Question to ask")
    parser.add_argument("--vector-store", default="faiss", choices=["faiss", "chromadb"],
                        help="Vector store backend")
    parser.add_argument("--url", default=os.getenv("TARGET_URL"),
                        help="URL to scrape (overrides saved content)")
    parser.add_argument("--content-dir", default="data/extracted_content",
                        help="Directory with pre-extracted content")
    parser.add_argument("--k", type=int, default=3, help="Number of docs to retrieve")

    args = parser.parse_args()

    rag = BasicRAG(vector_store_type=args.vector_store)

    if args.url:
        chunks = extract_content_from_url(args.url)
        save_chunks(chunks, args.content_dir)
        documents = chunks
    else:
        documents = rag.load_documents(args.content_dir)

    if not documents:
        print("No documents available. Use --url to fetch content first.")
        raise SystemExit(1)

    rag.create_vector_store(documents)
    answer = rag.query(args.query, k=args.k)
    print(f"\nAnswer:\n{answer}")
