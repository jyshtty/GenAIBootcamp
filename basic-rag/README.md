# 📚 Basic RAG Implementation - Assignment 1

**Target Audience:** Intermediate Level Developers  
**Focus:** Understanding RAG Fundamentals

## 🎯 Learning Objectives

By completing this assignment, you will:
- Build a basic **Retrieval-Augmented Generation (RAG)** system
- Understand **vector stores** and their importance
- Compare different **embedding models** and their trade-offs
- Practice web content extraction and processing
- Implement document chunking and retrieval strategies

## 📋 Prerequisites

- Python 3.11+ experience
- Basic understanding of LLMs and embeddings
- Familiarity with REST APIs
- Basic knowledge of vector databases

## 🚀 Quick Start

### 1. Environment Setup
```bash
# Clone and navigate to project
cd basic-rag

# Create virtual environment (use myenv or venv)
python -m venv myenv
# On Windows: myenv\Scripts\activate
# On Unix: source myenv/bin/activate

# Install dependencies
pip install -r requirements.txt
```
**Note (Windows):** If `pip install` fails with "No such file or directory" for long paths, enable [Windows Long Path support](https://pip.pypa.io/warnings/enable-long-paths) or clone/run the project from a shorter path (e.g. `C:\dev\basic-rag`).

### 2. Configuration
Create a `.env` file in the project root (copy from `.env.example` if present) with:
```env
DIAL_API_KEY=your_dial_api_key_here
TARGET_URL=https://example-website.com
```
Do not commit `.env` to version control.

**Getting your DIAL API Key:**
1. Obtain your API key from the EPAM Support
2. Replace `your_dial_api_key_here` with your actual key

### 3. Run the Basic RAG
```bash
# Extract and process content
python extract_content.py

# Run basic RAG queries
python basic_rag.py
```

## 📁 Project Structure

```
basic-rag/
├── README.md                 # Assignment documentation
├── requirements.txt          # Dependencies
├── .env.example             # Environment template
├── extract_content.py       # Web content extraction
├── basic_rag.py             # Main RAG implementation
├── vector_store_comparison.py # Compare different vector stores
├── embedding_comparison.py  # Compare embedding models
├── utils/
│   ├── __init__.py
│   └── dial_client.py       # EPAM DIAL API client
├── data/
│   ├── extracted_content/   # Processed documents
│   └── sample_urls.txt      # Sample URLs for testing
└── docs/
    └── rag_concepts.md      # RAG theory and concepts
```

## 🏗️ Core Requirements

### Phase 1: Content Extraction 

1. **Web Content Extraction**
   - Use `WebBaseLoader` to extract content from web pages
   - Implement content cleaning and preprocessing
   - Handle different content types (text, HTML)
   - Save extracted content for processing

2. **Document Processing**
   - Implement text chunking with overlap
   - Add metadata to chunks (source URL, chunk index)
   - Handle edge cases (empty content, large documents)

### Phase 2: Vector Store Implementation

3. **Vector Store Comparison**
   - Implement basic FAISS vector store
   - Implement ChromaDB vector store
   - **Compare performance, storage, and retrieval speed**
   - Document trade-offs between different vector stores

4. **Embedding Model Analysis**
   - Test with sentence-transformers (e.g., all-MiniLM-L6-v2)
   - **Compare embedding quality, speed, and cost**
   - Document when to use which embedding model

### Phase 3: RAG Implementation 
5. **Basic RAG System**
   - Implement similarity search
   - Build prompt template with retrieved context
   - Generate responses using **EPAM DIAL** API
   - Add basic error handling and DIAL client integration

6. **Testing and Evaluation**
   - Test with sample queries
   - Measure retrieval accuracy
   - Document system performance

## 🔧 Implementation Steps

### Step 1: Content Extraction
```python
# TODO: Implement in extract_content.py
# - Use WebBaseLoader for web scraping
# - Clean and chunk the extracted text
# - Save processed chunks
```

### Step 2: Vector Store Setup
```python
# TODO: Implement in vector_store_comparison.py
# - Setup FAISS vector store
# - Setup ChromaDB vector store
# - Compare indexing and retrieval performance
```

### Step 3: Embedding Comparison
```python
# TODO: Implement in embedding_comparison.py
# - Test OpenAI embeddings
# - Test sentence-transformers
# - Compare embedding quality and performance
```

### Step 4: RAG Implementation
```python
# TODO: Implement in basic_rag.py
# - Build retrieval mechanism
# - Create prompt templates
# - Generate responses using retrieved context
```

### Required Files
- ✅ `extract_content.py` - Working web content extraction
- ✅ `basic_rag.py` - Complete RAG implementation
- ✅ `vector_store_comparison.py` - FAISS vs ChromaDB analysis
- ✅ `embedding_comparison.py` - Embedding model comparison
- ✅ Analysis document answering key learning questions


## 🔧 Development Commands

```bash
# Extract content from sample URLs
python extract_content.py --url https://example.com

# Run vector store comparison
python vector_store_comparison.py

# Run embedding model comparison
python embedding_comparison.py

# Test basic RAG
python basic_rag.py --query "What is the main topic of the content?"
```
