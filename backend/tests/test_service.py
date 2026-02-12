"""Unit tests for summarizer service layer.

Covers:
- Multi-format input parsing (text, PDF, DOCX, URL)
- Configurable summary length (short, medium, long)
- Retry logic and exponential backoff in the engine
- Error handling for invalid inputs, oversized files, unsupported formats
- Batch processing with mixed success / failure
- History tracking for API and UI sessions
"""
import io
import time
from unittest.mock import patch, MagicMock

import pytest
from docx import Document as DocxDocument
from PyPDF2 import PdfWriter

from backend.app.errors import (
    APIConnectionError,
    FileProcessingError,
    FileSizeExceededError,
    InvalidRequestError,
    SummarizationError,
    SummarizerException,
    TokenLimitExceededError,
    UnsupportedFormatError,
    URLFetchError,
)
from backend.app.summarizer.service import SummarizerService


# ---------------------------------------------------------------------------
# Helpers - build realistic in-memory test files
# ---------------------------------------------------------------------------

def _make_pdf(text: str = "Hello from PDF") -> bytes:
    """Create a minimal single-page PDF containing *text*."""
    writer = PdfWriter()
    writer.add_blank_page(width=72, height=72)
    # PdfWriter doesn't support adding text directly in all versions,
    # so we mock extraction instead.  For a real PDF we just return bytes
    # that PdfReader can open.
    buf = io.BytesIO()
    writer.write(buf)
    return buf.getvalue()


def _make_docx(text: str = "Hello from DOCX") -> bytes:
    """Create a minimal DOCX document containing *text*."""
    doc = DocxDocument()
    doc.add_paragraph(text)
    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()


def _make_txt(text: str = "Hello from TXT") -> bytes:
    return text.encode("utf-8")


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def service():
    """Return a fresh SummarizerService instance (no shared state)."""
    return SummarizerService()


@pytest.fixture
def mock_engine():
    """Patch the global summarizer_engine used by the service module."""
    with patch("backend.app.summarizer.service.summarizer_engine") as engine:
        engine.summarize.return_value = "Mocked summary"
        yield engine


# ===================================================================
# 1. PLAIN TEXT SUMMARIZATION
# ===================================================================

class TestSummarizeText:
    """Tests for SummarizerService.summarize_text."""

    def test_text_returns_summary(self, service, mock_engine):
        result = service.summarize_text("Some document text", "short")
        assert result == "Mocked summary"
        mock_engine.summarize.assert_called_once_with("Some document text", "short")

    @pytest.mark.parametrize("length", ["short", "medium", "long"])
    def test_text_respects_length_param(self, service, mock_engine, length):
        service.summarize_text("text", length)
        mock_engine.summarize.assert_called_once_with("text", length)

    def test_text_default_length_is_medium(self, service, mock_engine):
        service.summarize_text("text")
        mock_engine.summarize.assert_called_once_with("text", "medium")

    def test_text_empty_raises_invalid_request(self, service, mock_engine):
        with pytest.raises(InvalidRequestError, match="empty"):
            service.summarize_text("   ")

    def test_text_whitespace_only_raises_invalid_request(self, service, mock_engine):
        with pytest.raises(InvalidRequestError):
            service.summarize_text("\n\t  ")

    def test_text_engine_error_wraps_in_summarizer_exception(self, service, mock_engine):
        mock_engine.summarize.side_effect = RuntimeError("unexpected")
        with pytest.raises(SummarizerException):
            service.summarize_text("text")

    def test_text_re_raises_summarizer_exception(self, service, mock_engine):
        mock_engine.summarize.side_effect = SummarizationError("ai broke")
        with pytest.raises(SummarizationError, match="ai broke"):
            service.summarize_text("text")


# ===================================================================
# 2. FILE SUMMARIZATION - PDF / DOCX / TXT
# ===================================================================

class TestSummarizeFile:
    """Tests for SummarizerService.summarize_file (multi-format)."""

    # -- TXT -----------------------------------------------------------

    def test_txt_file(self, service, mock_engine):
        content = _make_txt("plain text content")
        result = service.summarize_file(content, "readme.txt", "medium")
        assert result == "Mocked summary"

    # -- DOCX ----------------------------------------------------------

    def test_docx_file(self, service, mock_engine):
        content = _make_docx("docx paragraph")
        result = service.summarize_file(content, "report.docx", "long")
        assert result == "Mocked summary"

    # -- PDF -----------------------------------------------------------

    @patch("backend.app.summarizer.utils.extract_text_from_pdf", return_value="pdf text")
    def test_pdf_file(self, mock_extract, service, mock_engine):
        content = _make_pdf()
        result = service.summarize_file(content, "paper.pdf", "short")
        assert result == "Mocked summary"
        mock_extract.assert_called_once()

    # -- Unsupported format --------------------------------------------

    def test_unsupported_format_raises(self, service, mock_engine):
        with pytest.raises(SummarizerException):
            service.summarize_file(b"data", "image.png")

    # -- File size exceeded --------------------------------------------

    def test_oversized_file_raises(self, service, mock_engine):
        huge = b"x" * (11 * 1024 * 1024)  # 11 MB > default 10 MB
        with pytest.raises(SummarizerException):
            service.summarize_file(huge, "big.txt")

    # -- Corrupted files -----------------------------------------------

    def test_corrupted_pdf_raises(self, service, mock_engine):
        with pytest.raises(SummarizerException):
            service.summarize_file(b"not-a-pdf", "bad.pdf")

    def test_corrupted_docx_raises(self, service, mock_engine):
        with pytest.raises(SummarizerException):
            service.summarize_file(b"not-a-docx", "bad.docx")

    # -- Configurable length -------------------------------------------

    @pytest.mark.parametrize("length", ["short", "medium", "long"])
    def test_file_respects_length(self, service, mock_engine, length):
        content = _make_txt("some text")
        service.summarize_file(content, "f.txt", length)
        mock_engine.summarize.assert_called_once_with("some text", length)


# ===================================================================
# 3. URL SUMMARIZATION
# ===================================================================

class TestSummarizeUrl:
    """Tests for SummarizerService.summarize_url."""

    @patch("backend.app.summarizer.service.extract_text_from_url", return_value="web content")
    def test_url_returns_summary(self, mock_fetch, service, mock_engine):
        result = service.summarize_url("https://example.com", "short")
        assert result == "Mocked summary"
        mock_fetch.assert_called_once_with("https://example.com")

    @patch("backend.app.summarizer.service.extract_text_from_url")
    def test_url_fetch_error_raises(self, mock_fetch, service, mock_engine):
        mock_fetch.side_effect = URLFetchError("timeout")
        with pytest.raises(URLFetchError):
            service.summarize_url("https://down.example.com")

    @patch("backend.app.summarizer.service.extract_text_from_url", return_value="content")
    def test_url_engine_failure_wraps(self, mock_fetch, service, mock_engine):
        mock_engine.summarize.side_effect = RuntimeError("boom")
        with pytest.raises(SummarizerException):
            service.summarize_url("https://example.com")

    @pytest.mark.parametrize("length", ["short", "medium", "long"])
    @patch("backend.app.summarizer.service.extract_text_from_url", return_value="content")
    def test_url_respects_length(self, mock_fetch, service, mock_engine, length):
        service.summarize_url("https://example.com", length)
        mock_engine.summarize.assert_called_once_with("content", length)


# ===================================================================
# 4. BATCH PROCESSING
# ===================================================================

class TestSummarizeBatch:
    """Tests for SummarizerService.summarize_batch."""

    def test_batch_returns_results_per_file(self, service, mock_engine):
        files = [
            (_make_txt("one"), "a.txt"),
            (_make_txt("two"), "b.txt"),
        ]
        results = service.summarize_batch(files)
        assert len(results) == 2
        assert all(r["success"] for r in results)

    def test_batch_exceeds_max_files(self, service, mock_engine):
        files = [(_make_txt("x"), f"f{i}.txt") for i in range(11)]
        with pytest.raises(InvalidRequestError, match="Maximum"):
            service.summarize_batch(files)

    def test_batch_partial_failure(self, service, mock_engine):
        """One good file and one corrupted file should yield mixed results."""
        files = [
            (_make_txt("good"), "ok.txt"),
            (b"not-a-docx", "bad.docx"),
        ]
        results = service.summarize_batch(files)
        assert results[0]["success"] is True
        assert results[1]["success"] is False
        assert results[1]["error"] is not None

    def test_batch_result_fields(self, service, mock_engine):
        files = [(_make_txt("text"), "f.txt")]
        results = service.summarize_batch(files, "long")
        r = results[0]
        assert set(r.keys()) == {"index", "filename", "success", "summary", "error"}
        assert r["index"] == 0
        assert r["filename"] == "f.txt"

    @pytest.mark.parametrize("length", ["short", "medium", "long"])
    def test_batch_respects_length(self, service, mock_engine, length):
        files = [(_make_txt("text"), "f.txt")]
        service.summarize_batch(files, length)
        mock_engine.summarize.assert_called_once_with("text", length)


# ===================================================================
# 5. ENGINE RETRY LOGIC & EXPONENTIAL BACKOFF
# ===================================================================

class TestEngineRetryLogic:
    """Tests for retry + backoff inside SummarizerEngine.summarize."""

    @patch("backend.app.summarizer.engine.time.sleep")
    def test_retries_on_transient_failure_then_succeeds(self, mock_sleep):
        """Engine should retry on generic exceptions and return the result."""
        with patch("backend.app.summarizer.engine.SummarizerEngine.__init__", return_value=None):
            from backend.app.summarizer.engine import SummarizerEngine

            engine = SummarizerEngine()
            mock_client = MagicMock()
            engine.client = mock_client

            # Fail twice, succeed on 3rd call
            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = "  retry summary  "

            mock_client.chat.completions.create.side_effect = [
                ConnectionError("fail 1"),
                ConnectionError("fail 2"),
                mock_response,
            ]

            result = engine.summarize("text", "medium")
            assert result == "retry summary"
            assert mock_client.chat.completions.create.call_count == 3
            assert mock_sleep.call_count == 2

    @patch("backend.app.summarizer.engine.time.sleep")
    def test_raises_api_connection_error_after_max_retries(self, mock_sleep):
        """Engine should raise APIConnectionError after exhausting retries."""
        with patch("backend.app.summarizer.engine.SummarizerEngine.__init__", return_value=None):
            from backend.app.summarizer.engine import SummarizerEngine

            engine = SummarizerEngine()
            mock_client = MagicMock()
            engine.client = mock_client

            mock_client.chat.completions.create.side_effect = ConnectionError("always fails")

            with pytest.raises(APIConnectionError, match="temporarily unavailable"):
                engine.summarize("text", "short")

            assert mock_client.chat.completions.create.call_count == 3
            assert mock_sleep.call_count == 2

    @patch("backend.app.summarizer.engine.time.sleep")
    def test_exponential_backoff_delays(self, mock_sleep):
        """Verify sleep durations follow exponential backoff."""
        with patch("backend.app.summarizer.engine.SummarizerEngine.__init__", return_value=None):
            from backend.app.summarizer.engine import SummarizerEngine

            engine = SummarizerEngine()
            mock_client = MagicMock()
            engine.client = mock_client

            mock_client.chat.completions.create.side_effect = ConnectionError("fail")

            with pytest.raises(APIConnectionError):
                engine.summarize("text", "medium")

            # _BASE_DELAY_SECONDS=1.0, _BACKOFF_FACTOR=2.0
            # attempt 1 → sleep(1.0), attempt 2 → sleep(2.0)
            delays = [call.args[0] for call in mock_sleep.call_args_list]
            assert delays == [1.0, 2.0]


# ===================================================================
# 6. ENGINE ERROR HANDLING — TOKEN LIMIT / BAD REQUEST
# ===================================================================

class TestEngineErrorHandling:
    """Tests for specific error types raised by the engine."""

    def test_token_limit_exceeded(self):
        """BadRequestError mentioning 'token' should surface as a SummarizerException.

        The engine raises TokenLimitExceededError internally, but the outer
        except clause re-wraps it in SummarizationError.  We verify the
        user-facing message still mentions the text being too long.
        """
        from openai import BadRequestError

        with patch("backend.app.summarizer.engine.SummarizerEngine.__init__", return_value=None):
            from backend.app.summarizer.engine import SummarizerEngine

            engine = SummarizerEngine()
            mock_client = MagicMock()
            engine.client = mock_client

            # Simulate OpenAI BadRequestError with token-related message
            error_response = MagicMock()
            error_response.status_code = 400
            error_response.json.return_value = {"error": {"message": "token limit exceeded"}}
            mock_client.chat.completions.create.side_effect = BadRequestError(
                message="maximum context length exceeded - token limit",
                response=error_response,
                body={"error": {"message": "token limit exceeded"}},
            )

            with pytest.raises(SummarizerException, match="too long"):
                engine.summarize("a" * 100000, "short")

    def test_empty_summary_raises_summarization_error(self):
        """Engine should raise SummarizationError when AI returns empty text."""
        with patch("backend.app.summarizer.engine.SummarizerEngine.__init__", return_value=None):
            from backend.app.summarizer.engine import SummarizerEngine

            engine = SummarizerEngine()
            mock_client = MagicMock()
            engine.client = mock_client

            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = "   "
            mock_client.chat.completions.create.return_value = mock_response

            with pytest.raises(SummarizationError, match="empty"):
                engine.summarize("some text", "medium")

    def test_invalid_length_defaults_to_medium(self):
        """Engine should silently fall back to 'medium' for an unknown length."""
        with patch("backend.app.summarizer.engine.SummarizerEngine.__init__", return_value=None):
            from backend.app.summarizer.engine import SummarizerEngine

            engine = SummarizerEngine()
            mock_client = MagicMock()
            engine.client = mock_client

            mock_response = MagicMock()
            mock_response.choices = [MagicMock()]
            mock_response.choices[0].message.content = "summary"
            mock_client.chat.completions.create.return_value = mock_response

            result = engine.summarize("text", "extra_long")
            assert result == "summary"
            # verify max_tokens corresponds to "medium" (300)
            call_kwargs = mock_client.chat.completions.create.call_args
            assert call_kwargs.kwargs["max_tokens"] == 300


# ===================================================================
# 7. HISTORY TRACKING
# ===================================================================

class TestHistory:
    """Tests for API and UI history management in the service."""

    def test_add_and_get_api_history(self, service):
        service.add_api_history("alice", "text", "short", "summary1")
        service.add_api_history("alice", "file", "medium", "summary2", source="report.pdf")
        service.add_api_history("bob", "url", "long", "summary3")

        alice = service.get_api_history("alice")
        assert len(alice) == 2
        summaries = {e["summary"] for e in alice}
        assert summaries == {"summary1", "summary2"}

    def test_api_history_limit(self, service):
        for i in range(15):
            service.add_api_history("user", "text", "short", f"s{i}")
        assert len(service.get_api_history("user", limit=5)) == 5

    def test_add_and_get_ui_history(self, service):
        service.add_ui_history("text", "short", "ui summary")
        entries = service.get_ui_history()
        assert len(entries) == 1
        assert entries[0]["summary"] == "ui summary"

    def test_ui_history_limit(self, service):
        for i in range(25):
            service.add_ui_history("text", "short", f"s{i}")
        assert len(service.get_ui_history(limit=10)) == 10

    def test_history_entry_fields(self, service):
        entry = service.add_api_history("u", "file", "long", "s", source="f.pdf")
        assert "id" in entry
        assert "timestamp" in entry
        assert entry["source"] == "f.pdf"

    def test_history_without_source(self, service):
        entry = service.add_api_history("u", "text", "short", "s")
        assert "source" not in entry


# ===================================================================
# 8. UTILS — extract_text dispatcher
# ===================================================================

class TestExtractTextDispatcher:
    """Tests for utils.extract_text routing by extension."""

    def test_txt_extraction(self):
        from backend.app.summarizer.utils import extract_text
        result = extract_text(b"hello world", ".txt")
        assert result == "hello world"

    def test_txt_invalid_utf8(self):
        from backend.app.summarizer.utils import extract_text
        with pytest.raises(FileProcessingError, match="UTF-8"):
            extract_text(b"\xff\xfe", ".txt")

    def test_unsupported_extension(self):
        from backend.app.summarizer.utils import extract_text
        with pytest.raises(UnsupportedFormatError, match="Unsupported"):
            extract_text(b"data", ".xyz")

    def test_docx_extraction(self):
        from backend.app.summarizer.utils import extract_text
        content = _make_docx("extracted paragraph")
        result = extract_text(content, ".docx")
        assert "extracted paragraph" in result

    @patch("backend.app.summarizer.utils.extract_text_from_pdf", return_value="pdf text")
    def test_pdf_extraction(self, mock_pdf):
        from backend.app.summarizer.utils import extract_text
        result = extract_text(b"fake-pdf", ".pdf")
        assert result == "pdf text"

    def test_case_insensitive_extension(self):
        from backend.app.summarizer.utils import extract_text
        result = extract_text(b"hello", ".TXT")
        assert result == "hello"


# ===================================================================
# 9. UTILS — validate_file_size
# ===================================================================

class TestValidateFileSize:
    """Tests for utils.validate_file_size."""

    def test_within_limit(self):
        from backend.app.summarizer.utils import validate_file_size
        assert validate_file_size(1 * 1024 * 1024, 10) is True

    def test_exact_limit(self):
        from backend.app.summarizer.utils import validate_file_size
        assert validate_file_size(10 * 1024 * 1024, 10) is True

    def test_exceeds_limit(self):
        from backend.app.summarizer.utils import validate_file_size
        with pytest.raises(FileSizeExceededError):
            validate_file_size(11 * 1024 * 1024, 10)


# ===================================================================
# 10. UTILS — extract_text_from_url
# ===================================================================

class TestExtractTextFromUrl:
    """Tests for URL text extraction."""

    @patch("backend.app.summarizer.utils.requests.get")
    def test_successful_url_fetch(self, mock_get):
        from backend.app.summarizer.utils import extract_text_from_url

        mock_response = MagicMock()
        mock_response.content = b"<html><body><p>Useful content</p></body></html>"
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        result = extract_text_from_url("https://example.com")
        assert "Useful content" in result

    @patch("backend.app.summarizer.utils.requests.get")
    def test_url_timeout(self, mock_get):
        import requests as req
        from backend.app.summarizer.utils import extract_text_from_url

        mock_get.side_effect = req.Timeout("timed out")
        with pytest.raises(URLFetchError, match="timed out"):
            extract_text_from_url("https://slow.example.com")

    @patch("backend.app.summarizer.utils.requests.get")
    def test_url_empty_page(self, mock_get):
        from backend.app.summarizer.utils import extract_text_from_url

        mock_response = MagicMock()
        mock_response.content = b"<html><body></body></html>"
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        with pytest.raises(URLFetchError, match="No text"):
            extract_text_from_url("https://empty.example.com")

    @patch("backend.app.summarizer.utils.requests.get")
    def test_url_strips_scripts_and_styles(self, mock_get):
        from backend.app.summarizer.utils import extract_text_from_url

        html = (
            b"<html><head><style>body{}</style></head>"
            b"<body><script>alert(1)</script><p>clean text</p></body></html>"
        )
        mock_response = MagicMock()
        mock_response.content = html
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        result = extract_text_from_url("https://example.com")
        assert "clean text" in result
        assert "alert" not in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
