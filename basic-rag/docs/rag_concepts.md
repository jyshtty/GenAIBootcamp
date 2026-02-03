# RAG Concepts and Assignment Learnings

Short answers to the key learning questions from the Basic RAG assignment.

---

## 1. Trade-offs between FAISS and ChromaDB

- **Speed:** FAISS typically has faster indexing and query latency for in-memory use; ChromaDB adds persistence and metadata handling, so it can be slightly slower for raw similarity search.
- **Storage:** FAISS is in-memory by default; you can save/load index files to disk. ChromaDB persists by default to a directory (SQLite + vector index), so storage footprint is explicit and durable.
- **Persistence:** FAISS does not persist unless you call `save_local`/`load_local`; ChromaDB is built for persistence and multi-session use.
- **Scale:** FAISS scales well for large batches and single-node; ChromaDB is designed for embedding databases with optional filtering and multi-collection support.
- **When to use:** Use FAISS when you need maximum query speed and can rebuild or load the index at startup. Use ChromaDB when you need persistence, metadata filtering, or a long-lived embedding store.

---

## 2. Embedding models: dimension, speed, and quality

- **Dimension:** Higher dimensions (e.g. 768 vs 384) generally capture more nuance but increase storage and compute. all-MiniLM-L6-v2 and paraphrase-MiniLM-L3-v2 use 384 dimensions; all-mpnet-base-v2 uses 768.
- **Speed:** Smaller/faster models (e.g. paraphrase-MiniLM-L3-v2) encode faster; larger models (e.g. all-mpnet-base-v2) are slower but often yield better retrieval quality.
- **Quality:** Quality can be evaluated with query–document similarity tasks: correct pairs should have high cosine similarity; ranking correct docs above distractors indicates good retrieval. Trade off speed vs quality based on latency and accuracy requirements.

---

## 3. Chunk size and overlap

- **Chunk size:** Larger chunks preserve more context per chunk but can mix topics and dilute relevance; smaller chunks are more precise but may split sentences or ideas. Typical ranges are 500–1500 characters depending on document type.
- **Overlap:** Overlap (e.g. 200 characters) reduces boundary effects: a phrase at the edge of one chunk also appears in the next, so retrieval is less sensitive to where we cut. Too much overlap wastes storage and can duplicate context in the prompt.

---

## 4. How RAG improves over naive LLM-only answers

- **Groundedness:** RAG retrieves relevant passages and passes them as context, so the model answers from your data instead of relying only on its training. This reduces hallucination and keeps answers aligned with the corpus.
- **Up-to-date and domain-specific:** The index can be updated with new or domain docs; the model does not need retraining to use this content.
- **Traceability:** Retrieved chunks can be shown to the user or logged, so answers are explainable and auditable.
- **Pipeline:** Retrieve (top-k similar chunks) → augment (build a prompt with context + question) → generate (LLM produces the answer). This keeps the LLM focused on the provided context rather than generic knowledge.
