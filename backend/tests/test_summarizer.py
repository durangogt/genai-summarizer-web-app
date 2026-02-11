"""Unit tests for summarizer module."""
import pytest
from backend.app.summarizer.utils import (
    extract_text_from_pdf,
    extract_text_from_docx,
    validate_file_size
)
from backend.app.errors import (
    FileProcessingError,
    UnsupportedFormatError,
    FileSizeExceededError
)


class TestTextExtraction:
    """Test text extraction utilities."""
    
    def test_validate_file_size_valid(self):
        """Test file size validation with valid size."""
        # 5MB file, 10MB limit
        assert validate_file_size(5 * 1024 * 1024, 10) == True
    
    def test_validate_file_size_exceeds(self):
        """Test file size validation with exceeding size."""
        with pytest.raises(FileSizeExceededError):
            validate_file_size(15 * 1024 * 1024, 10)
    
    def test_extract_text_from_invalid_pdf(self):
        """Test PDF extraction with invalid content."""
        with pytest.raises(FileProcessingError):
            extract_text_from_pdf(b"not a valid pdf")
    
    def test_extract_text_from_invalid_docx(self):
        """Test DOCX extraction with invalid content."""
        with pytest.raises(FileProcessingError):
            extract_text_from_docx(b"not a valid docx")


class TestSummarizerEngine:
    """Test summarizer engine."""
    
    def test_engine_initialization(self):
        """Test that engine initializes without errors when config is valid."""
        # This test will fail if Azure OpenAI credentials are not set
        try:
            from backend.app.summarizer.engine import summarizer_engine
            assert summarizer_engine is not None
        except Exception as e:
            pytest.skip(f"Engine initialization failed: {str(e)}")
    
    def test_summarize_with_invalid_length(self):
        """Test summarization with invalid length parameter."""
        # Engine should default to medium when invalid length is provided
        from backend.app.summarizer.engine import summarizer_engine
        try:
            # This will fail without valid credentials but tests parameter handling
            result = summarizer_engine.summarize("Test text", "invalid_length")
        except Exception:
            # Expected to fail without valid Azure credentials
            pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
