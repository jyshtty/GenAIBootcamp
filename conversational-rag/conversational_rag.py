"""
Conversational RAG using LangChain ConversationalRetrievalChain + DIAL API.

Extends Assignment 1 by adding conversation memory so follow-up questions
are answered in context of the prior dialogue.

Example usage:
    python conversational_rag.py --session-id demo
    python conversational_rag.py --session-id demo --vector-store chromadb
"""

import os
import sys
import argparse
from typing import List, Optional

from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS, Chroma
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_classic.chains import ConversationalRetrievalChain
from langchain_classic.memory import ConversationBufferWindowMemory
from langchain_core.documents import Document

from chat_history import ChatHistoryManager
from message_trimming import MessageTrimmer

load_dotenv()

DIAL_API_KEY = os.getenv("DIAL_API_KEY", "")
DIAL_ENDPOINT = "https://ai-proxy.lab.epam.com"
DIAL_API_VERSION = "2025-04-01-preview"
DIAL_DEPLOYMENT = "gpt-5-mini-2025-08-07"
DEFAULT_EMBEDDING = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
MAX_HISTORY = int(os.getenv("MAX_HISTORY_LENGTH", "10"))


def _load_and_chunk(url: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[Document]:
    """Fetch a web page and split it into overlapping chunks."""
    loader = WebBaseLoader(url)
    docs = loader.load()
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_documents(docs)
    chunks = [c for c in chunks if c.page_content.strip()]
    print(f"Loaded {len(chunks)} chunks from {url}")
    return chunks


class ConversationalRAG:
    """Conversational RAG with persistent chat history and smart message trimming."""

    def __init__(
        self,
        vector_store_type: str = "faiss",
        embedding_model: str = DEFAULT_EMBEDDING,
        max_history: int = MAX_HISTORY,
    ):
        """
        Args:
            vector_store_type (str): "faiss" or "chromadb"
            embedding_model (str): sentence-transformer model name
            max_history (int): number of recent turns kept in LangChain memory window
        """
        self.vector_store_type = vector_store_type
        self.max_history = max_history

        # LLM via DIAL (Azure OpenAI endpoint)
        self.llm = AzureChatOpenAI(
            azure_endpoint=DIAL_ENDPOINT,
            api_key=DIAL_API_KEY,
            api_version=DIAL_API_VERSION,
            azure_deployment=DIAL_DEPLOYMENT,
        )

        # Embeddings
        self.embeddings = HuggingFaceEmbeddings(
            model_name=embedding_model,
            model_kwargs={"device": "cpu"},
        )

        self.vector_store = None
        self.qa_chain: Optional[ConversationalRetrievalChain] = None

        # History management
        self.history_manager = ChatHistoryManager(max_history=max_history * 2)
        self.trimmer = MessageTrimmer(
            max_tokens=3000,
            max_messages=max_history * 2,
            min_messages=2,
        )

        print(f"ConversationalRAG ready | store={vector_store_type} | model={embedding_model}")

    # ------------------------------------------------------------------
    # Setup
    # ------------------------------------------------------------------

    def setup(self, url: str):
        """
        Load content from URL, build vector store, and initialise the chain.

        Args:
            url (str): Web page to use as the knowledge base.
        """
        documents = _load_and_chunk(url)
        self._build_vector_store(documents)
        self._build_chain()

    def setup_from_documents(self, documents: List[Document]):
        """Alternative setup using pre-loaded Document objects."""
        self._build_vector_store(documents)
        self._build_chain()

    def _build_vector_store(self, documents: List[Document]):
        if not documents:
            raise ValueError("No documents to index.")
        if self.vector_store_type == "faiss":
            self.vector_store = FAISS.from_documents(documents, self.embeddings)
        else:
            self.vector_store = Chroma.from_documents(
                documents,
                self.embeddings,
                collection_name="conv_rag",
            )
        print(f"Vector store ({self.vector_store_type}) created with {len(documents)} docs.")

    def _build_chain(self):
        if not self.vector_store:
            raise RuntimeError("Call setup() before _build_chain().")

        memory = ConversationBufferWindowMemory(
            k=self.max_history,
            memory_key="chat_history",
            return_messages=True,
            output_key="answer",
        )
        self.qa_chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=self.vector_store.as_retriever(search_kwargs={"k": 3}),
            memory=memory,
            return_source_documents=True,
            verbose=False,
        )
        print("Conversation chain ready.")

    # ------------------------------------------------------------------
    # Chat
    # ------------------------------------------------------------------

    def chat(self, question: str, session_id: str = "default") -> dict:
        """
        Process a user question, maintaining history per session.

        Args:
            question (str): User's question.
            session_id (str): Session identifier for history isolation.

        Returns:
            dict: {"answer": str, "sources": list[str]}
        """
        if not self.qa_chain:
            return {"answer": "RAG not initialised. Call setup() first.", "sources": []}

        # Record user turn
        self.history_manager.add_message(session_id, "user", question)

        result = self.qa_chain({"question": question})
        answer = result.get("answer", "")
        source_docs = result.get("source_documents", [])
        sources = list({doc.metadata.get("source", "") for doc in source_docs if doc.metadata.get("source")})

        # Record assistant turn
        self.history_manager.add_message(session_id, "assistant", answer)

        return {"answer": answer, "sources": sources}

    def reset_session(self, session_id: str = "default"):
        """Clear memory for a session and rebuild the LangChain memory window."""
        self.history_manager.clear_session(session_id)
        if self.vector_store:
            self._build_chain()  # fresh memory window
        print(f"Session '{session_id}' reset.")

    def save_session(self, session_id: str):
        self.history_manager.save_session(session_id)

    def load_session(self, session_id: str) -> bool:
        return self.history_manager.load_session(session_id)

    def get_trimmed_history(self, session_id: str, strategy: str = "smart") -> List[dict]:
        """Return trimmed LangChain-compatible history for a session."""
        messages = self.history_manager.get_langchain_messages(session_id)
        if strategy == "smart":
            return self.trimmer.smart_trim(messages)
        elif strategy == "tokens":
            return self.trimmer.trim_by_tokens(messages)
        else:
            return self.trimmer.trim_by_count(messages)


# ------------------------------------------------------------------
# CLI interactive loop
# ------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Conversational RAG CLI")
    parser.add_argument("--session-id", default="cli_session", help="Session identifier")
    parser.add_argument("--url", default=os.getenv("TARGET_URL"), help="URL to load as knowledge base")
    parser.add_argument("--vector-store", default="faiss", choices=["faiss", "chromadb"])
    parser.add_argument("--embedding-model", default=DEFAULT_EMBEDDING)
    args = parser.parse_args()

    if not args.url:
        print("Provide --url or set TARGET_URL in .env")
        sys.exit(1)

    rag = ConversationalRAG(
        vector_store_type=args.vector_store,
        embedding_model=args.embedding_model,
    )
    rag.setup(args.url)

    print(f"\nConversational RAG ready. Session: {args.session_id}")
    print("Type 'quit' to exit, 'reset' to clear history, 'save' to persist session.\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_input:
            continue
        if user_input.lower() == "quit":
            break
        if user_input.lower() == "reset":
            rag.reset_session(args.session_id)
            print("Session cleared.\n")
            continue
        if user_input.lower() == "save":
            rag.save_session(args.session_id)
            continue

        response = rag.chat(user_input, session_id=args.session_id)
        print(f"\nAssistant: {response['answer']}")
        if response["sources"]:
            print(f"Sources: {', '.join(response['sources'])}")
        print()
