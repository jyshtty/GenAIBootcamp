# 🎯 RAG Assignments - Retrieval Augmented Generation Learning Path

**Target Audience:** Intermediate Level Developers  
**Focus:** Understanding and Building RAG Systems

## 📖 Overview

This learning path consists of two progressive assignments designed to teach Retrieval Augmented Generation (RAG) concepts from basic implementation to conversational systems.

## 🗂️ Assignments Structure

### Assignment 1: Basic RAG System
**Use Case:** Build a simple question-answering system that can extract information from web pages and answer user queries based on that content.

**What you'll learn:**
- Web content extraction using LangChain WebBaseLoader
- Vector stores comparison (FAISS vs ChromaDB)
- Embedding models analysis and selection
- Basic RAG pipeline implementation
- Document chunking and retrieval strategies

**Key Files to Implement:**
- `extract_content.py` - Web scraping and content processing
- `basic_rag.py` - Core RAG implementation
- `vector_store_comparison.py` - Compare vector databases
- `embedding_comparison.py` - Compare embedding models

### Assignment 2: Conversational RAG System  
**Use Case:** Extend Assignment 1 to create a chatbot that remembers conversation history and can handle follow-up questions in a natural conversational flow.

**What you'll learn:**
- Conversational memory using LangChain
- Chat history management and context preservation
- Message trimming for efficient token usage
- Streamlit web interface for chat interactions
- Context-aware retrieval and response generation

**Key Files to Implement:**
- `app.py` - Streamlit web interface
- `conversational_rag.py` - LangChain conversation chain
- `chat_history.py` - Session and history management
- `message_trimming.py` - Smart context trimming

## 🔄 How Assignment 2 Extends Assignment 1

Assignment 2 **directly builds** on Assignment 1 by:

1. **Reusing Core Components**: Vector store, embeddings, and content extraction from Assignment 1
2. **Adding Conversation Layer**: Wraps the basic RAG with conversation memory
3. **Enhancing User Experience**: Adds web interface and persistent chat sessions
4. **Optimizing Performance**: Implements smart message trimming for long conversations

**Progression Example:**
- **Assignment 1**: "What is the main topic of this website?" → Single answer
- **Assignment 2**: 
  - User: "What is the main topic of this website?"
  - Bot: "The website focuses on..."
  - User: "Can you elaborate on that?"
  - Bot: "Referring to my previous answer about [topic], here are more details..."

## 🛠️ Technical Stack

**Both Assignments Use:**
- **LangChain** for RAG pipeline and conversation management
- **EPAM DIAL API** for LLM responses
- **Vector Stores**: FAISS and ChromaDB for comparison
- **Embeddings**: Multiple models for analysis

**Assignment 2 Additionally Uses:**
- **Streamlit** for web interface
- **LangChain Memory** for conversation history
- **Message trimming** for token optimization

## 🚀 Getting Started

1. **Start with Assignment 1** - Build the foundation
2. **Complete Assignment 2** - Add conversational capabilities
3. **Compare and Analyze** - Document your learnings about vector stores, embeddings, and conversation patterns

## 📁 Folder Structure

```
RAGAssignments/
├── README.md                    # This overview file
├── basic-rag/                   # Assignment 1
│   ├── README.md               # Detailed Assignment 1 instructions
│   ├── extract_content.py      # TODO: Implement web scraping
│   ├── basic_rag.py           # TODO: Implement RAG system
│   ├── vector_store_comparison.py  # TODO: Compare FAISS vs ChromaDB
│   └── utils/dial_client.py    # DIAL API client (provided)
└── conversational-rag/         # Assignment 2
    ├── README.md               # Detailed Assignment 2 instructions
    ├── app.py                 # TODO: Implement Streamlit app
    ├── conversational_rag.py  # TODO: Implement conversation chain
    ├── chat_history.py        # TODO: Implement history management
    └── utils/dial_client.py    # DIAL API client (provided)
```

## 🔗 Key Resources

- [LangChain Documentation](https://python.langchain.com/)
- [EPAM DIAL Service](https://ai-proxy.lab.epam.com)
- [FAISS Documentation](https://faiss.ai/)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [Streamlit Documentation](https://docs.streamlit.io/)
