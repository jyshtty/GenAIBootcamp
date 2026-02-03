# streamlit ui - chat, sidebar for store/embedding, download chat

import os
import uuid
import streamlit as st
from dotenv import load_dotenv

from conversational_rag import answer
from chat_history import add_message, get_messages, clear_session, export_session
from vector_store import VECTOR_STORE_TYPES, EMBEDDING_MODELS
from message_trimming import count_tokens

load_dotenv()


def ensure_session() -> str:
    # make sure we have a session id
    if "session_id" not in st.session_state:
        st.session_state.session_id = str(uuid.uuid4())
    return st.session_state.session_id


def main():
    st.set_page_config(page_title="Conversational RAG", page_icon="💬", layout="wide")
    st.title("💬 Conversational RAG")
    st.caption("Ask questions over your documents with conversation memory.")

    with st.sidebar:
        st.header("Configuration")
        vector_store_type = st.selectbox(
            "Vector store",
            options=VECTOR_STORE_TYPES,
            index=0,
            help="FAISS: in-memory, fast. ChromaDB: persistent.",
        )
        embedding_model = st.selectbox(
            "Embedding model",
            options=EMBEDDING_MODELS,
            index=0,
            help="all-MiniLM-L6-v2: balance. paraphrase-MiniLM-L3-v2: faster, smaller.",
        )
        if st.button("New chat", use_container_width=True):
            clear_session(st.session_state.get("session_id", ""))
            st.session_state.session_id = str(uuid.uuid4())
            st.session_state.messages = []
            st.rerun()

        st.divider()
        session_id = ensure_session()
        st.text(f"Session: {session_id[:8]}...")

        msgs = get_messages(session_id, trim=False)
        if msgs:
            simple = [{"role": m.get("role", "user"), "content": m.get("content", "")} for m in msgs]
            try:
                tok_count = count_tokens(simple)
                st.caption(f"History: ~{tok_count} tokens")
            except Exception:
                pass
            lines = [f"# Chat session: {session_id[:8]}...\n\n"]
            for m in msgs:
                role = m.get("role", "user")
                ts = m.get("timestamp", "")
                content = m.get("content", "")
                lines.append(f"**{role}** ({ts})\n\n{content}\n\n")
            export_content = "".join(lines)
            st.download_button(
                "Download chat",
                data=export_content,
                file_name=f"chat_{session_id[:8]}.md",
                mime="text/markdown",
                use_container_width=True,
            )

    session_id = ensure_session()
    # show history from chat_history so timestamps appear
    msgs_to_show = get_messages(session_id, trim=False)
    for msg in msgs_to_show:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        ts = msg.get("timestamp", "")
        with st.chat_message(role):
            st.markdown(content)
            if ts:
                st.caption(ts)

    if prompt := st.chat_input("Ask a question about your documents"):
        if not os.getenv("DIAL_API_KEY") or os.getenv("DIAL_API_KEY") == "<YOUR_API_KEY_HERE>":
            st.error("Set DIAL_API_KEY in .env to use the RAG pipeline.")
            st.stop()

        with st.chat_message("user"):
            st.markdown(prompt)

        answer_text = ""
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    answer_text, retrieved_docs = answer(
                        session_id,
                        prompt,
                        vector_store_type=vector_store_type,
                        embedding_model_name=embedding_model,
                    )
                    st.markdown(answer_text)
                    if retrieved_docs:
                        with st.expander("Retrieved passages"):
                            for i, doc in enumerate(retrieved_docs[:5], 1):
                                st.text(doc[:500] + ("..." if len(doc) > 500 else ""))
                except FileNotFoundError as e:
                    st.error(str(e))
                except Exception as e:
                    st.error(f"Error: {e}")

        st.rerun()


if __name__ == "__main__":
    main()
