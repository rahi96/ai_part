"""
Navelle AI Module — File Parser
Downloads and extracts text from user documents (PDFs, etc).
"""
import logging
import io
import httpx
import pdfplumber
from typing import Optional

logger = logging.getLogger(__name__)

class FileParser:
    """Utilities for processing external files."""

    @staticmethod
    async def extract_text_from_url(url: str) -> Optional[str]:
        """
        Download a file from a URL and extract its text content.
        Currently supports PDF.
        """
        if not url:
            return None

        logger.info(f"Attempting to extract text from file: {url}")
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(url)
                response.raise_for_status()
                file_content = response.content

            # Check if it's a PDF
            if url.lower().endswith(".pdf") or response.headers.get("Content-Type") == "application/pdf":
                with pdfplumber.open(io.BytesIO(file_content)) as pdf:
                    text = ""
                    for page in pdf.pages:
                        page_text = page.extract_text()
                        if page_text:
                            text += page_text + "\n"
                    
                    if not text.strip():
                        logger.warning(f"No text extracted from PDF: {url}")
                        return "PDF file was read but no text could be extracted."
                        
                    return text.strip()
            
            else:
                logger.warning(f"Unsupported file type for URL: {url}")
                return "Unsupported file type (non-PDF)."

        except Exception as e:
            logger.error(f"Failed to extract text from {url}: {str(e)}")
            return f"Error reading file: {str(e)}"

# Singleton-like access
file_parser = FileParser()
