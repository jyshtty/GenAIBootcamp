"""
TODO: Implement basic RAG system using vector stores and DIAL API

Requirements:
1. Load processed content from extract_content.py
2. Create embeddings and populate vector store
3. Implement similarity search for retrieval
4. Build prompt template with retrieved context
5. Generate responses using EPAM DIAL API

Example usage:
    python basic_rag.py --query "What is the main topic of the content?"
"""

import os
import argparse
from dotenv import load_dotenv
from utils.dial_client import DIALClient

load_dotenv()

class BasicRAG:
    def __init__(self, vector_store_type="faiss"):
        """
        TODO: Initialize RAG system
        
        Args:
            vector_store_type (str): Type of vector store to use (faiss/chromadb)
        """
        self.dial_client = DIALClient()
        # TODO: Initialize vector store and embeddings
        pass
    
    def load_documents(self, content_dir: str = "data/extracted_content"):
        """
        TODO: Load processed documents from content directory
        
        Args:
            content_dir (str): Directory containing processed content
        """
        pass
    
    def create_vector_store(self, documents: list):
        """
        TODO: Create vector store from documents
        
        Args:
            documents (list): List of documents to index
        """
        pass
    
    def retrieve_relevant_docs(self, query: str, k: int = 3):
        """
        TODO: Retrieve relevant documents for query
        
        Args:
            query (str): User query
            k (int): Number of documents to retrieve
            
        Returns:
            list: List of relevant documents
        """
        pass
    
    def generate_response(self, query: str, retrieved_docs: list):
        """
        TODO: Generate response using DIAL API and retrieved context
        
        Args:
            query (str): User query
            retrieved_docs (list): Retrieved relevant documents
            
        Returns:
            str: Generated response
        """
        pass
    
    def query(self, query: str):
        """
        TODO: Complete RAG pipeline - retrieve and generate
        
        Args:
            query (str): User query
            
        Returns:
            str: Generated response
        """
        pass

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Basic RAG Question Answering")
    parser.add_argument("--query", required=True, help="Query to ask")
    parser.add_argument("--vector-store", default="faiss", choices=["faiss", "chromadb"], help="Vector store type")
    
    args = parser.parse_args()
    
    # TODO: Implement main execution logic
    print(f"TODO: Answer query: {args.query}")

