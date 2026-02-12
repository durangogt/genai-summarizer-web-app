"""Custom error classes and handlers for the application."""
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from backend.app.logger import app_logger


class SummarizerException(Exception):
    """Base exception for summarizer application."""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class FileProcessingError(SummarizerException):
    """Raised when file processing fails."""
    def __init__(self, message: str = "Failed to process file"):
        super().__init__(message, status_code=400)


class UnsupportedFormatError(SummarizerException):
    """Raised when file format is not supported."""
    def __init__(self, message: str = "Unsupported file format"):
        super().__init__(message, status_code=400)


class FileSizeExceededError(SummarizerException):
    """Raised when file size exceeds maximum limit."""
    def __init__(self, message: str = "File size exceeds maximum limit"):
        super().__init__(message, status_code=413)


class SummarizationError(SummarizerException):
    """Raised when summarization fails."""
    def __init__(self, message: str = "Failed to generate summary"):
        super().__init__(message, status_code=500)


class AuthenticationError(SummarizerException):
    """Raised when authentication fails."""
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status_code=401)


class InvalidRequestError(SummarizerException):
    """Raised when request is invalid."""
    def __init__(self, message: str = "Invalid request"):
        super().__init__(message, status_code=400)


class URLFetchError(SummarizerException):
    """Raised when fetching URL content fails."""
    def __init__(self, message: str = "Failed to fetch URL content"):
        super().__init__(message, status_code=400)


class SSLVerificationError(SummarizerException):
    """Raised when SSL certificate verification fails."""
    def __init__(self, message: str = "SSL certificate verification failed"):
        super().__init__(message, status_code=400)


class TokenLimitExceededError(SummarizerException):
    """Raised when input text exceeds model's token limit."""
    def __init__(self, message: str = "Input text is too long for the AI model"):
        super().__init__(message, status_code=400)


class APIConnectionError(SummarizerException):
    """Raised when the AI service is unreachable after retries."""
    def __init__(self, message: str = "The AI service is temporarily unavailable. Please try again later."):
        super().__init__(message, status_code=503)


# ---------------------------------------------------------------------------
# User-friendly message mapping
# ---------------------------------------------------------------------------

_USER_FRIENDLY_MESSAGES: dict[type, str] = {
    FileProcessingError: "We couldn't process your file. Please check that it is not corrupted and try again.",
    UnsupportedFormatError: "The uploaded file format is not supported. Please use PDF, DOCX, or TXT.",
    FileSizeExceededError: "The file is too large. Please upload a file smaller than the allowed limit.",
    SummarizationError: "We were unable to generate a summary at this time. Please try again later.",
    AuthenticationError: "Authentication failed. Please check your credentials and try again.",
    InvalidRequestError: "Your request could not be processed. Please check your input and try again.",
    URLFetchError: "We couldn't retrieve content from the provided URL. Please verify the URL and try again.",
    SSLVerificationError: "The URL has an untrusted SSL certificate. Please use a URL with a valid SSL certificate, or contact your administrator.",
    TokenLimitExceededError: "The input text is too long for the AI model to process. Please try with a shorter document or URL.",
    APIConnectionError: "The AI service is temporarily unavailable. Please try again in a few moments.",
}


def get_user_friendly_message(exc: Exception) -> str:
    """Return a user-friendly message for the given exception.

    Falls back to a generic message for unrecognised exception types.
    """
    for exc_type, message in _USER_FRIENDLY_MESSAGES.items():
        if isinstance(exc, exc_type):
            return message
    return "An unexpected error occurred. Please try again later."


async def summarizer_exception_handler(request: Request, exc: SummarizerException):
    """Handle custom summarizer exceptions."""
    app_logger.error(f"Error: {exc.message} | Status: {exc.status_code} | Path: {request.url.path}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.message,
            "status_code": exc.status_code
        }
    )


async def generic_exception_handler(request: Request, exc: Exception):
    """Handle generic exceptions."""
    app_logger.error(f"Unhandled exception: {str(exc)} | Path: {request.url.path}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "An unexpected error occurred. Please try again later.",
            "status_code": 500
        }
    )
