# grabs text from url and chunk it for RAG

import os
import re
import json
import argparse
from pathlib import Path

from dotenv import load_dotenv
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.documents import Document

load_dotenv()


def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200):
    """split text into chunks with bit of overlap so we dont cut mid sentence"""
    if not text or not text.strip():
        return []
    text = text.strip()
    if len(text) <= chunk_size:
        return [text]
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        if end >= len(text):
            break
        start = end - overlap
    return chunks


def clean_text(text: str) -> str:
    """just normalize whitespace and newlines"""
    if not text:
        return ""
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\n\s*\n", "\n\n", text)
    return text.strip()


def extract_content_from_url(url: str, chunk_size: int = 1000, overlap: int = 200):
    """load page from url, clean it, chunk it and add metadata to each chunk"""
    loader = WebBaseLoader([url])
    documents = loader.load()
    if not documents:
        return []
    full_text = "\n\n".join(doc.page_content for doc in documents)
    cleaned = clean_text(full_text)
    if not cleaned:
        return []
    raw_chunks = chunk_text(cleaned, chunk_size=chunk_size, overlap=overlap)
    result = []
    total = len(raw_chunks)
    for i, content in enumerate(raw_chunks):
        result.append(
            Document(
                page_content=content,
                metadata={
                    "source_url": url,
                    "chunk_index": i,
                    "total_chunks": total,
                },
            )
        )
    return result


def save_chunks(chunks: list, output_dir: str = "data/extracted_content"):
    """write chunks to a json file so basic_rag can load them later"""
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    out_path = Path(output_dir) / "chunks.json"
    data = []
    for doc in chunks:
        data.append(
            {
                "content": doc.page_content,
                "metadata": doc.metadata,
            }
        )
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return str(out_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract content from web pages")
    parser.add_argument("--url", required=True, help="URL to extract content from")
    parser.add_argument("--output", default="data/extracted_content", help="Output directory")
    parser.add_argument("--chunk-size", type=int, default=1000, help="Chunk size in characters")
    parser.add_argument("--overlap", type=int, default=200, help="Overlap between chunks")

    args = parser.parse_args()

    print(f"Extracting content from {args.url}...")
    try:
        chunks = extract_content_from_url(
            args.url, chunk_size=args.chunk_size, overlap=args.overlap
        )
    except Exception as e:
        print(f"Error extracting content: {e}")
        raise SystemExit(1)

    if not chunks:
        print("Warning: No content extracted (empty page or extraction failed).")
        raise SystemExit(0)

    out_path = save_chunks(chunks, args.output)
    print(f"Saved {len(chunks)} chunks to {out_path}")
