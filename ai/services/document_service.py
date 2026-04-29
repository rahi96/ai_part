from __future__ import annotations
import logging
from typing import Any
from ai.utils.backend_client import backend_client
from ai.utils.document_processor import process_cloudinary_file

logger = logging.getLogger(__name__)


class DocumentService:
    async def ingest_user_documents(self, user_id: str) -> dict:
        logger.info("Starting document ingestion for user %s", user_id)
        files = await backend_client.get_user_files(user_id)
        logger.info("Raw files from backend for user %s: %s", user_id, files)

        if not files:
            logger.warning("No files found for user %s", user_id)
            return {
                "user_id": user_id,
                "files_found": 0,
                "files_processed": 0,
                "chunks": [],
                "errors": ["No files found. Check BACKEND_URL in .env and ensure the backend is running."],
            }

        all_chunks: list[dict] = []
        processed_files = 0
        errors: list[str] = []

        for file_info in files:
            file_url = file_info.get("url") or file_info.get("secure_url")
            file_name = file_info.get("name", "unknown")
            file_id = str(file_info.get("_id", file_info.get("id", "unknown")))
            file_type = file_info.get("type", "DOC")

            if not file_url:
                errors.append(f"Missing URL for file {file_name}")
                continue

            try:
                chunks = process_cloudinary_file(
                    file_url=file_url,
                    file_name=file_name,
                    file_id=file_id,
                    file_type=file_type,
                )
                logger.info("Extracted %d chunks from %s", len(chunks), file_name)

                if chunks:
                    all_chunks.extend(chunks)
                    processed_files += 1
                else:
                    errors.append(f"No text extracted from {file_name}")
            except Exception as exc:
                logger.error("Failed to process %s: %s", file_name, exc)
                errors.append(f"{file_name}: {exc}")

        logger.info(
            "Ingestion complete for user %s: %d files, %d chunks",
            user_id,
            processed_files,
            len(all_chunks),
        )

        return {
            "user_id": user_id,
            "files_found": len(files),
            "files_processed": processed_files,
            "chunks": all_chunks,
            "errors": errors,
        }
