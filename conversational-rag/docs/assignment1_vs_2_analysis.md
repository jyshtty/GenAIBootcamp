# Assignment 1 vs Assignment 2: Learnings Comparison

## Assignment 1 (Basic RAG)

- **Single-turn QA**: One question in, one answer out. No memory of previous questions or answers.
- **Components**: Web extraction, chunking, vector store (FAISS/ChromaDB), embedding models, retriever, DIAL for generation.
- **Focus**: Choosing vector store and embedding model; implementing retrieve-then-generate pipeline.
- **Output**: Answer grounded in retrieved chunks only; no conversation context.

## Assignment 2 (Conversational RAG)

- **Multi-turn conversation**: Chat history is kept; follow-up questions can refer to earlier answers (e.g. "Can you elaborate on that?").
- **New components**:
  - **Chat history**: Per-session storage with timestamps; used as context for the LLM.
  - **Message trimming**: Token-aware trimming so long conversations stay within model limits (e.g. keep last N turns or summarize older ones).
  - **Streamlit UI**: Sidebar for vector store and embedding model; chat interface; session export.
  - **LangChain-style flow**: Retriever + prompt built from context + chat history + question; DIAL wrapped as a LangChain chat model for consistency.
- **Focus**: Context preservation, token management, and UX (session reset, download chat).
- **Output**: Answer that can reference "our conversation" and previous answers; optional display of retrieved passages and session export.

## Summary

| Aspect            | Assignment 1        | Assignment 2                          |
|------------------|---------------------|----------------------------------------|
| Turns            | Single              | Multi-turn with history                |
| Context          | Retrieved docs only | Retrieved docs + chat history          |
| Token handling   | N/A                 | Trimming strategies                   |
| Interface        | CLI                 | Streamlit web app                      |
| Session          | N/A                 | Session ID, reset, export              |
| Follow-up questions | Not supported    | Supported via history                  |

## Takeaways

- Conversational RAG extends basic RAG by adding a **memory layer** (chat history) and **trimming** so that context stays manageable.
- The same vector store and embedding choices from Assignment 1 apply; Assignment 2 adds **runtime switching** in the UI.
- **History-aware retrieval** (rewriting the user question using conversation context) can be added on top for even better follow-up handling.
