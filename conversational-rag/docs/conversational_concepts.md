# Conversational RAG Concepts

## Chat history

- Messages are stored per **session** (e.g. session ID from Streamlit or CLI).
- Each entry has **role** (user/assistant), **content**, and **timestamp**.
- History is passed into the prompt so the model can refer to previous answers (e.g. "as I said earlier", "elaborating on that...").

## Message trimming

- LLMs have a **context window** (token limit). Long conversations must be trimmed.
- **Strategies**:
  - **last_n**: Keep only the last N message pairs (user + assistant).
  - **last_n_drop**: Same as last_n; older messages are dropped.
  - **last_n_summarize**: Keep last N and replace older turns with a short summary placeholder.
- **MAX_HISTORY_LENGTH** (env) controls how many pairs to keep; **tiktoken** is used to count tokens.

## Context-aware retrieval

- In a minimal setup, retrieval uses only the **current question**.
- Optionally, the system can **rewrite** the question using chat history (e.g. "What is X?" after "Tell me about Y" becomes "What is X in the context of Y?") so the retriever returns more relevant chunks. This is often done with a small LLM call or a dedicated prompt.

## Flow

1. User sends a message.
2. **Chat history** (optionally trimmed) is loaded for the session.
3. **Retriever** fetches top-k documents for the current question (or a history-aware query).
4. **Prompt** is built: system instructions + conversation so far + retrieved context + current question.
5. **LLM** (DIAL) generates the answer.
6. **History** is updated with the user message and the assistant reply.
7. Answer (and optionally retrieved passages) is shown in the UI.

## Session and export

- Each chat has a **session_id**. "New chat" creates a new session and clears history for the UI and the in-memory store.
- **Export** writes the current session’s messages (with timestamps) to a file (JSON or Markdown) under `data/chat_sessions/`.
