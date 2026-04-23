"""
Navelle AI Module — Document Ingestion Routes
Fetches user files from Cloudinary, extracts text, and returns chunks.
No vector database — chunks are returned for direct prompt use.
"""
from __future__ import annotations

import logging

from fastapi import APIRouter, HTTPException, Path

from ai.services.document_service import DocumentService
from ai.utils.backend_client import backend_client

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/ai/documents", tags=["Documents"])

_service = DocumentService()


@router.post("/ingest/{user_id}")
async def ingest_user_documents(
    user_id: str = Path(..., description="MongoDB ObjectId of the user"),
):
    """
    Fetch all user files from the backend (Cloudinary URLs), extract text,
    and return text chunks for direct use in prompts.
    """
    try:
        result = await _service.ingest_user_documents(user_id)
        return {
            "user_id": user_id,
            "status": "success" if not result["errors"] else "partial_success",
            "files_found": result["files_found"],
            "files_processed": result["files_processed"],
            "chunks": result["chunks"],
            "errors": result["errors"],
        }
    except Exception as exc:
        logger.error("Document ingestion failed for user %s: %s", user_id, exc)
        raise HTTPException(
            status_code=500,
            detail=f"Document ingestion failed: {exc}",
        )
