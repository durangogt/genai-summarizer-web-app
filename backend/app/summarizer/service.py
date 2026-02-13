"""Summarizer service layer for all AI summarization and input parsing logic.

This service encapsulates text extraction (PDF, DOCX, URL, plain text),
file validation, AI-powered summarization, and history management.
The API and UI layers should delegate all summarization work to this service.
"""
import os
from datetime import datetime
from typing import Literal, Optional

from backend.app.config import config
from backend.app.logger import app_logger
from backend.app.errors import (
    InvalidRequestError,
    SummarizerException,
    get_user_friendly_message,
)
from backend.app.summarizer.utils import (
    extract_text,
    extract_text_from_url,
    validate_file_size,
)
from backend.app.summarizer.engine import summarizer_engine


class SummarizerService:
    """Central service for summarization operations and history tracking."""

    def __init__(self):
        """Initialize history stores for API and UI sessions."""
        self.api_history: list[dict] = []
        self.ui_history: list[dict] = []

    # ------------------------------------------------------------------
    # Core summarization helpers
    # ------------------------------------------------------------------

    def summarize_text(
        self,
        text: str,
        length: Literal["short", "medium", "long"] = "medium",
    ) -> str:
        """Validate and summarize plain text.

        Args:
            text: Raw text to summarize.
            length: Desired summary length.

        Returns:
            Generated summary string.

        Raises:
            InvalidRequestError: If the text is empty.
            SummarizerException: With a user-friendly message on failure.
        """
        if not text.strip():
            raise InvalidRequestError("Text cannot be empty")

        try:
            app_logger.info(f"Generating {length} summary for text input")
            return summarizer_engine.summarize(text, length)
        except SummarizerException:
            raise
        except Exception as e:
            app_logger.error(f"Text summarization failed unexpectedly: {str(e)}")
            raise SummarizerException(get_user_friendly_message(e))

    def summarize_file(
        self,
        file_content: bytes,
        filename: str,
        length: Literal["short", "medium", "long"] = "medium",
    ) -> str:
        """Validate, extract text from a file, and summarize.

        Supports PDF, DOCX, and TXT formats.

        Args:
            file_content: Raw file bytes.
            filename: Original filename (used for extension detection).
            length: Desired summary length.

        Returns:
            Generated summary string.

        Raises:
            SummarizerException: With a user-friendly message on failure.
        """
        try:
            validate_file_size(len(file_content), config.MAX_FILE_SIZE_MB)
            file_extension = os.path.splitext(filename)[1].lower()
            text = extract_text(file_content, file_extension)

            app_logger.info(f"Generating {length} summary for file: {filename}")
            return summarizer_engine.summarize(text, length)
        except SummarizerException:
            raise
        except Exception as e:
            app_logger.error(f"File summarization failed for {filename}: {str(e)}")
            raise SummarizerException(get_user_friendly_message(e))

    def summarize_url(
        self,
        url: str,
        length: Literal["short", "medium", "long"] = "medium",
    ) -> str:
        """Fetch content from a URL, extract text, and summarize.

        Args:
            url: Web URL to fetch and summarize.
            length: Desired summary length.

        Returns:
            Generated summary string.

        Raises:
            SummarizerException: With a user-friendly message on failure.
        """
        try:
            text = extract_text_from_url(url)

            app_logger.info(f"Generating {length} summary for URL: {url}")
            return summarizer_engine.summarize(text, length)
        except SummarizerException:
            raise
        except Exception as e:
            app_logger.error(f"URL summarization failed for {url}: {str(e)}")
            raise SummarizerException(get_user_friendly_message(e))

    def summarize_batch(
        self,
        files: list[tuple[bytes, str]],
        length: Literal["short", "medium", "long"] = "medium",
        user_id: str = "system",
    ) -> list[dict]:
        """Validate and summarize a batch of files.

        Args:
            files: List of (file_content_bytes, filename) tuples.
            length: Desired summary length for all files.
            user_id: User identifier for audit logging.

        Returns:
            List of result dicts with keys: index, filename, success, summary, error.

        Raises:
            InvalidRequestError: If batch size exceeds the configured limit.
        """
        from backend.app.logger import log_audit_event
        
        # Log batch start
        log_audit_event(
            action="batch_summarization",
            user_id=user_id,
            status="started",
            details={
                "batch_size": len(files),
                "summary_length": length,
                "filenames": [f for _, f in files]
            }
        )
        
        if len(files) > config.MAX_BATCH_FILES:
            error_msg = f"Maximum {config.MAX_BATCH_FILES} files allowed per batch"
            log_audit_event(
                action="batch_summarization",
                user_id=user_id,
                status="failed",
                details={"batch_size": len(files)},
                error=error_msg
            )
            raise InvalidRequestError(error_msg)

        results: list[dict] = []
        for idx, (content, filename) in enumerate(files):
            try:
                app_logger.info(
                    f"Processing batch item {idx + 1}/{len(files)}: "
                    f"user_id={user_id}, filename={filename}"
                )
                summary = self.summarize_file(content, filename, length)
                results.append(
                    {
                        "index": idx,
                        "filename": filename,
                        "success": True,
                        "summary": summary,
                        "error": None,
                    }
                )
                log_audit_event(
                    action="batch_item_processed",
                    user_id=user_id,
                    status="success",
                    details={
                        "batch_index": idx,
                        "filename": filename,
                        "summary_length": len(summary)
                    }
                )
            except Exception as e:
                friendly = get_user_friendly_message(e)
                results.append(
                    {
                        "index": idx,
                        "filename": filename,
                        "success": False,
                        "summary": None,
                        "error": friendly,
                    }
                )
                log_audit_event(
                    action="batch_item_processed",
                    user_id=user_id,
                    status="failed",
                    details={
                        "batch_index": idx,
                        "filename": filename
                    },
                    error=f"{str(e)} | User-friendly: {friendly}"
                )

        # Log batch completion
        successful_count = sum(1 for r in results if r["success"])
        failed_count = sum(1 for r in results if not r["success"])
        
        log_audit_event(
            action="batch_summarization",
            user_id=user_id,
            status="success" if failed_count == 0 else "partial_success",
            details={
                "total_files": len(files),
                "successful": successful_count,
                "failed": failed_count,
                "success_rate": f"{(successful_count/len(files)*100):.1f}%"
            }
        )
        
        return results

    # ------------------------------------------------------------------
    # History helpers
    # ------------------------------------------------------------------

    def add_api_history(
        self,
        user: str,
        source_type: str,
        length: str,
        summary: str,
        source: Optional[str] = None,
    ) -> dict:
        """Record a summarization entry in API history.

        Args:
            user: Username from the JWT token.
            source_type: One of 'text', 'file', 'url'.
            length: Summary length used.
            summary: Generated summary text.
            source: Optional source identifier (filename or URL).

        Returns:
            The newly created history entry dict.
        """
        entry: dict = {
            "id": len(self.api_history) + 1,
            "user": user,
            "type": source_type,
            "length": length,
            "summary": summary,
            "timestamp": datetime.utcnow(),
        }
        if source is not None:
            entry["source"] = source
        self.api_history.append(entry)
        return entry

    def get_api_history(self, username: str, limit: int = 10) -> list[dict]:
        """Retrieve API history for a specific user.

        Args:
            username: The user whose history to retrieve.
            limit: Maximum number of entries to return.

        Returns:
            List of history entries, most recent first.
        """
        user_entries = [e for e in self.api_history if e["user"] == username]
        return sorted(user_entries, key=lambda x: x["timestamp"], reverse=True)[:limit]

    def add_ui_history(
        self,
        source_type: str,
        length: str,
        summary: str,
        source: Optional[str] = None,
    ) -> dict:
        """Record a summarization entry in UI history.

        Args:
            source_type: One of 'text', 'file', 'url'.
            length: Summary length used.
            summary: Generated summary text.
            source: Optional source identifier (filename or URL).

        Returns:
            The newly created history entry dict.
        """
        entry: dict = {
            "id": len(self.ui_history) + 1,
            "type": source_type,
            "length": length,
            "summary": summary,
            "timestamp": datetime.utcnow(),
        }
        if source is not None:
            entry["source"] = source
        self.ui_history.append(entry)
        return entry

    def get_ui_history(self, limit: int = 20) -> list[dict]:
        """Retrieve recent UI history entries.

        Args:
            limit: Maximum number of entries to return.

        Returns:
            List of history entries, most recent first.
        """
        return sorted(self.ui_history, key=lambda x: x["timestamp"], reverse=True)[:limit]


# Global service instance shared across API and UI
summarizer_service = SummarizerService()
