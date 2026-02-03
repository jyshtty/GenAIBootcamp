# vector store - faiss or chroma, can switch embedding model too

import json
from pathlib import Path
from typing import List, Optional

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS, Chroma
from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStoreRetriever


EMBEDDING_MODELS = ["all-MiniLM-L6-v2", "paraphrase-MiniLM-L3-v2"]
VECTOR_STORE_TYPES = ["faiss", "chromadb"]


def load_documents(content_dir: str = "data/extracted_content") -> List[Document]:
    # read chunks.json, give back list of docs
    path = Path(content_dir) / "chunks.json"
    if not path.exists():
        raise FileNotFoundError(
            f"No chunks found at {path}. Copy chunks.json from basic-rag/data/extracted_content "
            "or run extract_content.py --url <URL> first."
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


class VectorStoreManager:
    # can switch faiss/chroma and embedding model at runtime

    def __init__(
        self,
        vector_store_type: str = "faiss",
        embedding_model_name: str = "all-MiniLM-L6-v2",
        content_dir: str = "data/extracted_content",
        chroma_persist_dir: Optional[str] = None,
    ):
        self.vector_store_type = vector_store_type
        self.embedding_model_name = embedding_model_name
        self.content_dir = content_dir
        self.chroma_persist_dir = chroma_persist_dir or "data/chroma_db"
        self._embeddings = HuggingFaceEmbeddings(model_name=embedding_model_name)
        self._vector_store = None
        self._documents: Optional[List[Document]] = None

    def _ensure_documents(self) -> List[Document]:
        if self._documents is None:
            self._documents = load_documents(self.content_dir)
        return self._documents

    def build(self) -> None:
        # build or rebuild index with current settings
        documents = self._ensure_documents()
        if not documents:
            raise ValueError("No documents to index.")
        if self.vector_store_type == "faiss":
            self._vector_store = FAISS.from_documents(documents, self._embeddings)
        elif self.vector_store_type == "chromadb":
            Path(self.chroma_persist_dir).mkdir(parents=True, exist_ok=True)
            self._vector_store = Chroma.from_documents(
                documents,
                self._embeddings,
                persist_directory=self.chroma_persist_dir,
                collection_name="conversational_rag",
            )
        else:
            raise ValueError(
                f"Unknown vector_store_type: {self.vector_store_type}. "
                f"Use one of {VECTOR_STORE_TYPES}"
            )

    def switch(
        self,
        vector_store_type: Optional[str] = None,
        embedding_model_name: Optional[str] = None,
    ) -> None:
        # switch store or embedding, then rebuild
        if vector_store_type is not None:
            if vector_store_type not in VECTOR_STORE_TYPES:
                raise ValueError(f"Use one of {VECTOR_STORE_TYPES}")
            self.vector_store_type = vector_store_type
        if embedding_model_name is not None:
            if embedding_model_name not in EMBEDDING_MODELS:
                raise ValueError(f"Use one of {EMBEDDING_MODELS}")
            self.embedding_model_name = embedding_model_name
            self._embeddings = HuggingFaceEmbeddings(model_name=self.embedding_model_name)
        self._vector_store = None
        self.build()

    def get_retriever(self, k: int = 3, **kwargs) -> VectorStoreRetriever:
        # retriever for current store
        if self._vector_store is None:
            self.build()
        return self._vector_store.as_retriever(
            search_kwargs={"k": k, **kwargs}
        )

    def similarity_search(self, query: str, k: int = 3) -> List[Document]:
        # find top k docs for query
        if self._vector_store is None:
            self.build()
        return self._vector_store.similarity_search(query, k=k)
