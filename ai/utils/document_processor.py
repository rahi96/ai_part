"""
Navelle AI Module — Document Processor
Downloads files from Cloudinary URLs, extracts text, and chunks for LLM context.
Supports PDF and plain-text files.
"""
from __future__ import annotations

import io
import logging
import tempfile
from pathlib import Path
from typing import Any

import httpx
import pdfplumber

logger = logging.getLogger(__name__)

# ── File download ────────────────────────────────────────────────────────────


def _download_file(url: str) -> bytes | None:
    """Download a file from a Cloudinary (or any) URL."""
    try:
        resp = httpx.get(url, timeout=60, follow_redirects=True)
        resp.raise_for_status()
        return resp.content
    except Exception as exc:
        logger.error("Failed to download file from %s: %s", url, exc)
        return None


# ── Text extraction ────────────────────────────────────────────────────────────


def _extract_pdf_text(data: bytes) -> str:
    """Extract text from a PDF byte blob using pdfplumber."""
    text_parts: list[str] = []
    try:
        with pdfplumber.open(io.BytesIO(data)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
    except Exception as exc:
        logger.error("PDF text extraction failed: %s", exc)
        return ""
    return "\n\n".join(text_parts)


def _extract_text(file_name: str, data: bytes) -> str | None:
    """Route to the correct extractor based on file extension."""
    ext = Path(file_name).suffix.lower()
    if ext == ".pdf":
        return _extract_pdf_text(data)
    elif ext in (".txt", ".md", ".csv", ".json"):
        try:
            return data.decode("utf-8")
        except UnicodeDecodeError:
            logger.warning("Could not decode %s as UTF-8", file_name)
            return None
    else:
        logger.warning("Unsupported file type for ingestion: %s", ext)
        return None


# ── Chunking ───────────────────────────────────────────────────────────────────


def _chunk_text(
    text: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
) -> list[str]:
    """Split text into overlapping chunks using a simple recursive splitter."""
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    return splitter.split_text(text)


# ── Public API ─────────────────────────────────────────────────────────────────


def process_cloudinary_file(
    file_url: str,
    file_name: str,
    file_id: str,
    file_type: str = "DOC",
) -> list[dict]:
    """
    Download a file from Cloudinary, extract text, and return chunks.

    Args:
        file_url: Public Cloudinary URL
        file_name: Original file name (used for type detection)
        file_id: Unique document ID from MongoDB
        file_type: Document category (DOC, LAB, etc.)

    Returns:
        List of chunk dicts ready for direct LLM context injection.
    """
    data = _download_file(file_url)
    if not data:
        return []

    raw_text = _extract_text(file_name, data)
    if not raw_text or not raw_text.strip():
        logger.warning("No text extracted from %s", file_name)
        return []

    chunks = _chunk_text(raw_text)
    if not chunks:
        return []

    total = len(chunks)
    result: list[dict] = []
    for idx, chunk_text in enumerate(chunks, start=1):
        result.append(
            {
                "id": f"{file_id}_chunk_{idx}",
                "document_id": file_id,
                "document_title": file_name,
                "document_type": file_type,
                "category": "user_upload",
                "chunk_index": idx,
                "total_chunks": total,
                "content": chunk_text.strip(),
                "metadata": {"source_url": file_url},
            }
        )

    logger.info(
        "Processed %s → %d chunks (%d chars total)",
        file_name,
        total,
        len(raw_text),
    )
    return result
