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
