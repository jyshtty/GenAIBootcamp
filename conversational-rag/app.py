"""
Streamlit Conversational RAG Web Interface.

Provides a chat UI backed by the ConversationalRAG engine.
Users can switch vector stores, embedding models, and web sources
from the sidebar without restarting.

Run:
    streamlit run app.py
"""

import os
import json
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv

from conversational_rag import ConversationalRAG
from message_trimming import MessageTrimmer

load_dotenv()

# ------------------------------------------------------------------
# Page config
# ------------------------------------------------------------------

st.set_page_config(
    page_title="Conversational RAG",
    page_icon="🤖",
    layout="wide",
)

# ------------------------------------------------------------------
# Session-state initialisation
# ------------------------------------------------------------------

def _init_state():
    defaults = {
        "messages": [],          # {"role": str, "content": str, "timestamp": str, "sources": list}
        "rag": None,
        "initialized": False,
        "session_id": f"session_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
        "current_url": "",
        "current_store": "faiss",
        "current_model": "all-MiniLM-L6-v2",
        "token_count": 0,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

_init_state()

trimmer = MessageTrimmer(max_tokens=3000)

# ------------------------------------------------------------------
# Sidebar
# ------------------------------------------------------------------

with st.sidebar:
    st.title("⚙️ Configuration")
    st.markdown("---")

    url = st.text_input(
        "Knowledge Base URL",
        value=os.getenv("TARGET_URL", "https://en.wikipedia.org/wiki/Machine_learning"),
        help="Web page to use as the RAG knowledge base.",
    )

    vector_store = st.selectbox(
        "Vector Store",
        options=["faiss", "chromadb"],
        index=0,
        help="FAISS: fast in-memory. ChromaDB: persistent with metadata filtering.",
    )

    embedding_model = st.selectbox(
        "Embedding Model",
        options=["all-MiniLM-L6-v2", "all-mpnet-base-v2"],
        index=0,
        help="all-MiniLM-L6-v2: fast 384d. all-mpnet-base-v2: accurate 768d.",
    )

    max_history = st.slider(
        "Max Conversation History (turns)",
        min_value=2,
        max_value=20,
        value=int(os.getenv("MAX_HISTORY_LENGTH", "10")),
    )

    trimming_strategy = st.selectbox(
        "Message Trimming Strategy",
        options=["smart", "tokens", "last_n"],
        index=0,
        help="How to trim history when it exceeds token limits.",
    )

    init_btn = st.button("🚀 Initialize / Reload RAG", use_container_width=True)
    reset_btn = st.button("🔄 Reset Conversation", use_container_width=True)

    st.markdown("---")
    st.caption(f"Session: `{st.session_state.session_id}`")

    # Download chat history
    if st.session_state.messages:
        history_json = json.dumps(st.session_state.messages, indent=2)
        st.download_button(
            label="⬇️ Download Chat History",
            data=history_json,
            file_name=f"{st.session_state.session_id}.json",
            mime="application/json",
            use_container_width=True,
        )

    if st.session_state.initialized:
        st.success(f"✅ Ready — {vector_store} / {embedding_model}")
        msgs = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
        st.caption(f"~{trimmer.count_tokens(msgs)} tokens in history")

# ------------------------------------------------------------------
# Initialise / reload RAG
# ------------------------------------------------------------------

if init_btn:
    config_changed = (
        url != st.session_state.current_url
        or vector_store != st.session_state.current_store
        or embedding_model != st.session_state.current_model
    )
    if config_changed or not st.session_state.initialized:
        with st.spinner("Loading content and building vector index…"):
            try:
                rag = ConversationalRAG(
                    vector_store_type=vector_store,
                    embedding_model=embedding_model,
                    max_history=max_history,
                )
                rag.setup(url)
                st.session_state.rag = rag
                st.session_state.initialized = True
                st.session_state.current_url = url
                st.session_state.current_store = vector_store
                st.session_state.current_model = embedding_model
                st.session_state.messages = []
                st.success("RAG system ready!")
            except Exception as e:
                st.error(f"Initialisation failed: {e}")
    else:
        st.info("Configuration unchanged — no reload needed.")

if reset_btn and st.session_state.rag:
    st.session_state.rag.reset_session(st.session_state.session_id)
    st.session_state.messages = []
    st.success("Conversation cleared.")

# ------------------------------------------------------------------
# Main chat area
# ------------------------------------------------------------------

st.title("🤖 Conversational RAG")
st.caption("Ask questions about the loaded web page. Follow-up questions use conversation history.")

if not st.session_state.initialized:
    st.info("👈 Enter a URL in the sidebar and click **Initialize / Reload RAG** to start.")
else:
    # Render message history
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("sources"):
                with st.expander("📄 Sources", expanded=False):
                    for src in msg["sources"]:
                        st.caption(src)

    # Chat input
    if user_input := st.chat_input("Ask a question…"):
        # Display user message
        with st.chat_message("user"):
            st.markdown(user_input)

        st.session_state.messages.append({
            "role": "user",
            "content": user_input,
            "timestamp": datetime.utcnow().isoformat(),
            "sources": [],
        })

        # Apply trimming before querying (keeps context window sane)
        raw_msgs = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
        if trimming_strategy == "smart":
            trimmed = trimmer.smart_trim(raw_msgs)
        elif trimming_strategy == "tokens":
            trimmed = trimmer.trim_by_tokens(raw_msgs)
        else:
            trimmed = trimmer.trim_by_count(raw_msgs)
        _ = trimmed  # available for debugging; chain uses its own memory window

        # Generate response
        with st.chat_message("assistant"):
            with st.spinner("Thinking…"):
                try:
                    response = st.session_state.rag.chat(
                        user_input,
                        session_id=st.session_state.session_id,
                    )
                    answer = response["answer"]
                    sources = response.get("sources", [])
                except Exception as e:
                    answer = f"Error: {e}"
                    sources = []

            st.markdown(answer)
            if sources:
                with st.expander("📄 Sources", expanded=False):
                    for src in sources:
                        st.caption(src)

        st.session_state.messages.append({
            "role": "assistant",
            "content": answer,
            "timestamp": datetime.utcnow().isoformat(),
            "sources": sources,
        })

# ------------------------------------------------------------------
# Footer
# ------------------------------------------------------------------

st.markdown("---")
st.caption(
    "Assignment 2 — Conversational RAG | "
    "EPAM DIAL API · LangChain · FAISS / ChromaDB · Streamlit"
)
