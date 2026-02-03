# Conversational RAG – Application Guide

Everything about this app: what it does, how to run it, and example outputs.

---

## What is this app

Its a chatbot that answer questions from your documents. It remember the conversation so you can ask follow-ups like "can you elaborate" or "what about that thing you said earlier". You can use it in the browser (Streamlit) or from the command line.

---

## Features

### 1. Chat over your documents
- You ask a question. The app find the most relevant chunks from your content (from `data/extracted_content/chunks.json`) and send them + your question to the LLM (DIAL). You get a answer based on that context.
- If you dont have chunks yet, copy `chunks.json` from the basic-rag project or run extract_content from basic-rag first.

### 2. Conversation memory
- Each chat has a session. The app keep the last N turns (user + assistant) in memory so the model can refer to previous answers. Good for follow-up questions.
- You can start a "New chat" anytime to clear the history and get a fresh session.

### 3. Message trimming
- Long conversations would hit token limits. So we trim: we keep only the last few message pairs (or summarize older ones). Configurable via env `MAX_HISTORY_LENGTH` (default 10 pairs).

### 4. Vector store and embedding choice
- **Vector store:** FAISS (in-memory, fast) or ChromaDB (persistent, saved to disk). You can switch in the UI or CLI.
- **Embedding model:** `all-MiniLM-L6-v2` (good balance) or `paraphrase-MiniLM-L3-v2` (faster/smaller). Same switch in UI or CLI.

### 5. Streamlit UI
- Main area: chat messages, you type and get answers.
- Sidebar: pick vector store, embedding model, "New chat" button, session id, and "Download chat" to save the conversation as markdown.
- Each answer can show "Retrieved passages" in a expander so you see what chunks was used.

### 6. CLI (no browser)
- Run a single question from terminal. Useful for testing or scripts.
- Export a session to a file (json or markdown) from command line.

### 7. Session export
- From the UI: "Download chat" gives you a markdown file of the current session.
- From CLI: `python chat_history.py --export SESSION_ID` writes to `data/chat_sessions/`.

---

## Setup

### 1. Virtual env and dependencies
```bash
cd conversational-rag
python -m venv myenv
# Windows:
myenv\Scripts\activate
# Linux/Mac:
# source myenv/bin/activate
pip install -r requirements.txt
```

### 2. Config
Create a `.env` in the project root (or copy from `.env.example`):

```
DIAL_API_KEY=your_actual_key_here
TARGET_URL=https://example.com
MAX_HISTORY_LENGTH=10
```

You need a valid `DIAL_API_KEY` from EPAM to get real answers. Without it the app will tell you to set it.

### 3. Content
Put your document chunks in `data/extracted_content/chunks.json`. Same format as basic-rag (list of `{ "content": "...", "metadata": {...} }`). If you already did Assignment 1, just copy that folder or the file.

---

## How to run

### Option A: Streamlit (web UI)
```bash
# from project root, with venv activated
streamlit run app.py
```
Then open the URL it prints (usually http://localhost:8501). Type in the chat box and hit enter.

### Option B: Command line (one question)
```bash
python conversational_rag.py --session-id my-session --query "What is the main topic?"
```
Optional flags:
- `--vector-store faiss` or `chromadb`
- `--embedding all-MiniLM-L6-v2` or `paraphrase-MiniLM-L3-v2`
- `--content-dir data/extracted_content`

### Option C: Message trimming test
```bash
python message_trimming.py --test
```
Prints before/after token counts for a long fake history.

### Option D: Export a session from CLI
```bash
python chat_history.py --export YOUR_SESSION_ID --format md
```
Writes to `data/chat_sessions/session_YOUR_SESSION_ID.md` (or .json if you use `--format json`).

---

## Example runs and outputs

### Example 1: Streamlit – first question
**You type:** What is this website about?

**App does:** Loads chunks, search for relevant ones, send context + question to DIAL, show answer.

**Example output (assistant):**  
"This website is for use in documentation examples. It is not meant for real use in operations. You can learn more from the content provided."

**Retrieved passages (expander):**  
Shows the chunk(s) that was used (e.g. the "Example Domain" text).

---

### Example 2: Streamlit – follow-up
**You type:** Can you say that in one sentence?

**App does:** Same flow but now "Conversation so far" in the prompt include your previous Q and the previous answer. So the model can say something like: "This site is only for documentation examples and should not be used in real operations."

---

### Example 3: CLI – single query
**Command:**
```bash
python conversational_rag.py --session-id cli-test --query "What is the main topic?"
```

**Example output (stdout):**
```
This domain is for use in documentation examples without needing permission. Avoid use in operations. Learn more.
```

**If you add the optional docs print (already in script):**
```
--- Retrieved passages (first 200 chars each) ---
1. Example DomainExample DomainThis domain is for use in documentation examples...
```

---

### Example 4: No DIAL key
**Command:**  
Same as above but without `DIAL_API_KEY` in `.env`.

**Output:**
```
Set DIAL_API_KEY in .env to use the RAG pipeline.
```
Then exit code 1.

---

### Example 5: No chunks file
**Command:**  
Run app or CLI without `data/extracted_content/chunks.json`.

**Output (error):**  
FileNotFoundError saying something like: "No chunks found at ... Copy chunks.json from basic-rag ... or run extract_content.py --url <URL> first."

---

### Example 6: Message trimming test
**Command:**
```bash
python message_trimming.py --test
```

**Example output:**
```
Before trim: 30 messages, ~5430 tokens
After trim (last_n, max_history_length=5): 10 messages, ~1810 tokens
After trim (last_n_summarize, max_history_length=5): 11 messages, ~1827 tokens
Test passed.
```

---

### Example 7: Chat history export
**Command:**
```bash
python chat_history.py
```
**Output:**
```
Sessions: []
Use --export SESSION_ID to export a session.
```

After you had a chat in Streamlit (so a session exist), you can do:
```bash
python chat_history.py --export abc12345-xxxx-xxxx-xxxx --format md
```
**Output:**
```
Exported to data/chat_sessions/session_abc12345-xxxx-xxxx-xxxx.md
```

---

## File layout (main pieces)

| File / folder | What it does |
|----------------|---------------|
| `app.py` | Streamlit UI – chat, sidebar, download |
| `conversational_rag.py` | Main logic: get history, retrieve docs, call DIAL, save history |
| `vector_store.py` | Load chunks, build FAISS or Chroma, search |
| `message_trimming.py` | Trim chat history by tokens / length |
| `chat_history.py` | Store and get messages per session, export |
| `utils/dial_client.py` | Call DIAL API |
| `utils/dial_llm.py` | LangChain wrapper so DIAL can be used in chain |
| `data/extracted_content/chunks.json` | Your document chunks (you provide or copy from basic-rag) |
| `data/chat_sessions/` | Exported sessions (md or json) |
| `.env` | DIAL_API_KEY, MAX_HISTORY_LENGTH, etc. |

---

## Troubleshooting

- **"Set DIAL_API_KEY"**  
  Add `DIAL_API_KEY=your_key` to `.env`.

- **"No chunks found"**  
  Create `data/extracted_content/chunks.json` or copy from basic-rag.

- **Slow first answer**  
  First run load embeddings and build the vector index; later ones are faster.

- **Answer not using my doc**  
  Check that chunks.json has the right content and that your question match the vocabulary in the chunks (retrieval is semantic similarity).

Thats it – you got all the details about features, running the app, and example outputs in one place.
