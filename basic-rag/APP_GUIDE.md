# Basic RAG – Application Guide

Everything about what this app does, how to run it, and what output you get.

---

## What this app does (features)

1. **Extract content from a URL**  
   Give it a webpage URL and it will grab the text, clean it, split it into chunks (with overlap), and save them to a JSON file. That file is what the RAG part uses later.

2. **Compare embedding models**  
   Runs two sentence-transformers models (all-MiniLM-L6-v2 and paraphrase-MiniLM-L3-v2), measures speed (time per text), quality (query–document similarity), and dimension. Prints a short report and recommendation.

3. **Compare vector stores (FAISS vs ChromaDB)**  
   Builds both indexes from the same documents, times how long indexing takes, runs a bunch of queries to get average query time, and compares storage (bytes). Prints a report and when to use which.

4. **Ask questions and get answers (RAG)**  
   Loads the chunks you extracted, builds a vector store (FAISS or ChromaDB), finds the top chunks for your question, and sends them plus the question to the DIAL API to get an answer. So you ask in natural language and get an answer based on your content.

---

## Setup

- **Python:** 3.11 or higher.
- **Virtual env:** From the `basic-rag` folder:
  ```bash
  python -m venv myenv
  # Windows:
  myenv\Scripts\activate
  # Linux/Mac:
  source myenv/bin/activate
  ```
- **Dependencies:**
  ```bash
  pip install -r requirements.txt
  ```
  If on Windows you get an error about “No such file or directory” and a very long path, turn on [Windows long path support](https://pip.pypa.io/warnings/enable-long-paths) or move the project to a short path (e.g. `C:\dev\basic-rag`) and run `pip install` again.

- **Config:** Create a `.env` in the project root with:
  ```env
  DIAL_API_KEY=your_actual_key_here
  TARGET_URL=https://example-website.com
  ```
  You need `DIAL_API_KEY` for the RAG part (asking questions). Get the key from EPAM support. Don’t commit `.env`.

---

## How to run (with examples)

### 1. Extract content from a URL

**Example:**
```bash
python extract_content.py --url https://example.com
```

**Optional arguments:**
- `--output` – folder where to save chunks (default: `data/extracted_content`)
- `--chunk-size` – characters per chunk (default: 1000)
- `--overlap` – overlap between chunks (default: 200)

**Example with options:**
```bash
python extract_content.py --url https://example.com --output data/extracted_content --chunk-size 500 --overlap 100
```

**Example output:**
```
Extracting content from https://example.com...
Saved 1 chunks to data\extracted_content\chunks.json
```
(You might see a USER_AGENT message; you can ignore it.)

---

### 2. Embedding comparison

**Example:**
```bash
python embedding_comparison.py
```

First run can download the models. Then it prints dimensions, speed, quality, and a short recommendation.

**Example output:**
```
=== Embedding Model Comparison Report ===

Dimensions:
  all-MiniLM-L6-v2: 384
  paraphrase-MiniLM-L3-v2: 384

Speed (avg seconds per text, batch of 10):
  all-MiniLM-L6-v2: 0.0123s
  paraphrase-MiniLM-L3-v2: 0.0098s

Quality (mean correct query-doc similarity, accuracy):
  all-MiniLM-L6-v2: mean_similarity=0.7234, accuracy=1.00
  paraphrase-MiniLM-L3-v2: mean_similarity=0.6891, accuracy=1.00

--- Recommendation ---
  all-MiniLM-L6-v2: Good balance of speed and quality; smaller dimension (384). Use for fast retrieval.
  paraphrase-MiniLM-L3-v2: Smaller/faster model (384 dim); use when latency is critical.
  For best quality on semantic similarity, consider all-mpnet-base-v2 (768 dim, slower).
```

---

### 3. Vector store comparison (FAISS vs ChromaDB)

**Example:**
```bash
python vector_store_comparison.py
```

If `data/extracted_content/chunks.json` exists, it uses those chunks; otherwise it uses built-in sample docs. Prints indexing time, query time, and storage.

**Example output:**
```
=== Vector Store Comparison Report ===

Using 1 documents from data\extracted_content\chunks.json

Indexing performance (time to build index):
  faiss: 0.065s
  chromadb: 0.567s

Query performance (avg over 50 runs, query='What is machine learning?...'):
  faiss: 13.24 ms per query
  chromadb: 16.58 ms per query

Storage (bytes):
  faiss: 2075 bytes (2.0 KB)
  chromadb: 336036 bytes (328.2 KB)

--- Recommendation ---
  FAISS: Faster indexing and query; in-memory or save/load from disk. Best for single-node, large batches.
  ChromaDB: Persistent by default; good for multi-session apps and when you need metadata filtering.
```

---

### 4. RAG – ask a question

You must have run **extract content** at least once so `data/extracted_content/chunks.json` exists, and `DIAL_API_KEY` must be set in `.env`.

**Example (FAISS):**
```bash
python basic_rag.py --query "What is the main topic of the content?" --vector-store faiss
```

**Example (ChromaDB):**
```bash
python basic_rag.py --query "What is this website about?" --vector-store chromadb
```

**Optional:**
- `--content-dir` – folder that contains `chunks.json` (default: `data/extracted_content`)

**Example with custom content dir:**
```bash
python basic_rag.py --query "Summarize the content." --content-dir data/extracted_content --vector-store faiss
```

**Example output (for https://example.com):**
```
The main topic of the content is that the domain "Example Domain" is intended for use in documentation examples and should not be used in operations.
```

Another run might give:
```
The context does not provide detailed information about the website's content. It only states that the domain is for use in documentation examples and is not intended for operational use.
```

**If something goes wrong:**
- No `chunks.json`: you get something like  
  `Error: No chunks found at data\extracted_content\chunks.json. Run extract_content.py --url <URL> first.`
- Missing or invalid `DIAL_API_KEY`:  
  `Error: Set DIAL_API_KEY in .env to use the RAG pipeline.`

**Windows and emoji:** If you see `UnicodeEncodeError` when running the RAG script (e.g. in DIAL client messages), set UTF-8 for the console before running, e.g. in PowerShell:
```powershell
$env:PYTHONIOENCODING='utf-8'
python basic_rag.py --query "What is the main topic?" --vector-store faiss
```

---

## Example outputs summary

| What you run | What you see |
|--------------|--------------|
| `extract_content.py --url https://example.com` | “Saved N chunks to … chunks.json” |
| `embedding_comparison.py` | Report: dimensions, speed (s per text), quality (similarity/accuracy), recommendation |
| `vector_store_comparison.py` | Report: indexing time (s), query time (ms), storage (bytes/KB), recommendation |
| `basic_rag.py --query "..." --vector-store faiss` | One paragraph answer based on your extracted content |

For more on RAG concepts and trade-offs, see `docs/rag_concepts.md`.
