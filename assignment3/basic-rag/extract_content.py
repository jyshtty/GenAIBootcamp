"""
Web content extraction using LangChain WebBaseLoader.

Loads a page, splits it into overlapping chunks, and optionally saves
them as JSON files for later use by the RAG pipeline.

Example usage:
    python extract_content.py --url https://en.wikipedia.org/wiki/Machine_learning
"""

import os
import re
import json
import argparse
from dotenv import load_dotenv
from langchain_community.document_loaders import WebBaseLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

load_dotenv()


def extract_content_from_url(url: str, chunk_size: int = 1000, chunk_overlap: int = 200):
    """
    Load a web page and split it into overlapping chunks.

    Args:
        url (str): Website URL to extract content from
        chunk_size (int): Maximum characters per chunk
        chunk_overlap (int): Overlap between consecutive chunks

    Returns:
        list: LangChain Document objects with page_content and metadata
    """
    print(f"Loading content from {url}...")
    loader = WebBaseLoader(url)
    docs = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_documents(docs)

    # Remove empty/whitespace-only chunks
    chunks = [c for c in chunks if c.page_content.strip()]
    print(f"Created {len(chunks)} chunks from {url}")
    return chunks


def clean_text(text: str) -> str:
    """Normalize whitespace and strip; return "" for empty/None input."""
    if not text:
        return ""
    return re.sub(r"\s+", " ", text).strip()


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200):
    """
    Split raw text into overlapping string chunks.

    Args:
        text (str): Text to chunk
        chunk_size (int): Size of each chunk
        overlap (int): Overlap between chunks

    Returns:
        list[str]: Chunked text strings; empty list if input is blank.
    """
    if not text or not text.strip():
        return []
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    return splitter.split_text(text)


def save_chunks(chunks: list, output_dir: str = "data/extracted_content"):
    """
    Save document chunks as a single chunks.json file (JSON array of {content, metadata}).

    Args:
        chunks (list): LangChain Document objects
        output_dir (str): Directory to write chunks.json into
    """
    os.makedirs(output_dir, exist_ok=True)
    payload = [
        {"content": c.page_content, "metadata": c.metadata}
        for c in chunks
    ]
    path = os.path.join(output_dir, "chunks.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    print(f"Saved {len(chunks)} chunks to '{path}'")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract content from web pages")
    parser.add_argument("--url", default=os.getenv("TARGET_URL"), help="URL to extract content from")
    parser.add_argument("--output", default="data/extracted_content", help="Output directory")
    parser.add_argument("--chunk-size", type=int, default=1000)
    parser.add_argument("--chunk-overlap", type=int, default=200)

    args = parser.parse_args()
    if not args.url:
        parser.error("Provide --url or set TARGET_URL in .env")

    chunks = extract_content_from_url(args.url, args.chunk_size, args.chunk_overlap)
    save_chunks(chunks, args.output)
    print(f"Done. {len(chunks)} chunks saved to '{args.output}'")
