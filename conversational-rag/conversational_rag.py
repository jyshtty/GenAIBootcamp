# conversational rag - retrieval + chat history, then dial for answer

import os
import argparse
from typing import List, Optional, Tuple

from dotenv import load_dotenv

from vector_store import VectorStoreManager, load_documents
from chat_history import add_message, get_messages, clear_session
from message_trimming import trim_messages
from utils.dial_llm import DIALChatModel

load_dotenv()

DEFAULT_CONTENT_DIR = "data/extracted_content"
SYSTEM_PROMPT = (
    "You are a helpful assistant that answers questions based on the provided context. "
    "Use the context below and the conversation history to answer. "
    "If the context does not contain the answer, say so. "
    "For follow-up questions, refer to previous answers when relevant."
)


def _format_chat_history(messages: List[dict]) -> str:
    # turn history into string for prompt
    if not messages:
        return ""
    lines = []
    for m in messages:
        role = m.get("role", "user")
        content = m.get("content", "")
        label = "Human" if role == "user" else "Assistant"
        lines.append(f"{label}: {content}")
    return "\n".join(lines)


def answer(
    session_id: str,
    question: str,
    vector_store_type: str = "faiss",
    embedding_model_name: str = "all-MiniLM-L6-v2",
    content_dir: str = DEFAULT_CONTENT_DIR,
    k_retrieve: int = 3,
    max_history_length: Optional[int] = None,
) -> Tuple[str, List[str]]:
    # get trimmed history, retrieve docs, call llm, save to history. returns answer + retrieved texts
    max_history_length = max_history_length or int(os.getenv("MAX_HISTORY_LENGTH", "10"))

    history_messages = get_messages(session_id, trim=True, max_history_length=max_history_length)
    chat_history_str = _format_chat_history(history_messages)

    vs_manager = VectorStoreManager(
        vector_store_type=vector_store_type,
        embedding_model_name=embedding_model_name,
        content_dir=content_dir,
    )
    retrieved_docs = vs_manager.similarity_search(question, k=k_retrieve)
    context = "\n\n".join(doc.page_content for doc in retrieved_docs)
    retrieved_contents = [doc.page_content for doc in retrieved_docs]

    if chat_history_str:
        user_content = (
            "Conversation so far:\n"
            f"{chat_history_str}\n\n"
            "Relevant context from documents:\n"
            f"{context}\n\n"
            f"Question: {question}\n\n"
            "Answer based on the context and conversation:"
        )
    else:
        user_content = (
            "Relevant context from documents:\n"
            f"{context}\n\n"
            f"Question: {question}\n\n"
            "Answer based on the context:"
        )

    llm = DIALChatModel(model="gpt-4")
    from langchain_core.messages import HumanMessage, SystemMessage
    messages = [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=user_content),
    ]
    response = llm.invoke(messages)

    answer_text = response.content if hasattr(response, "content") else str(response)

    add_message(session_id, "user", question)
    add_message(session_id, "assistant", answer_text)

    return answer_text, retrieved_contents


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Conversational RAG (no UI)")
    parser.add_argument("--session-id", default="cli-session", help="Chat session ID")
    parser.add_argument("--query", "-q", help="Single question to ask")
    parser.add_argument("--vector-store", default="faiss", choices=["faiss", "chromadb"])
    parser.add_argument("--embedding", default="all-MiniLM-L6-v2", choices=["all-MiniLM-L6-v2", "paraphrase-MiniLM-L3-v2"])
    parser.add_argument("--content-dir", default=DEFAULT_CONTENT_DIR)
    args = parser.parse_args()

    if not os.getenv("DIAL_API_KEY") or os.getenv("DIAL_API_KEY") == "<YOUR_API_KEY_HERE>":
        print("Set DIAL_API_KEY in .env to use the RAG pipeline.")
        raise SystemExit(1)

    if args.query:
        try:
            ans, docs = answer(
                args.session_id,
                args.query,
                vector_store_type=args.vector_store,
                embedding_model_name=args.embedding,
                content_dir=args.content_dir,
            )
            print(ans)
            if docs:
                print("\n--- Retrieved passages (first 200 chars each) ---")
                for i, d in enumerate(docs[:3], 1):
                    print(f"{i}. {d[:200]}...")
        except FileNotFoundError as e:
            print(f"Error: {e}")
            raise SystemExit(1)
        except Exception as e:
            print(f"Error: {e}")
            raise SystemExit(1)
    else:
        print("Usage: python conversational_rag.py --session-id test123 --query 'Your question'")
