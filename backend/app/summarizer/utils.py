"""Text extraction utilities for PDF, DOCX, and web URLs."""
import io
import ssl
from typing import Optional
import requests
from requests.exceptions import SSLError
import urllib3
from PyPDF2 import PdfReader
from docx import Document
from bs4 import BeautifulSoup
from backend.app.config import config
from backend.app.errors import (
    FileProcessingError,
    UnsupportedFormatError,
    URLFetchError,
    SSLVerificationError,
)
from backend.app.logger import app_logger

# Disable SSL warnings when SSL verification is disabled
if not config.VERIFY_SSL_CERTIFICATES:
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    app_logger.warning("SSL certificate verification is disabled. This is insecure for production use.")


def extract_text_from_pdf(file_content: bytes) -> str:
    """
    Extract text from PDF file.
    
    Args:
        file_content: PDF file content as bytes
        
    Returns:
        Extracted text as string
        
    Raises:
        FileProcessingError: If PDF processing fails
    """
    try:
        pdf_file = io.BytesIO(file_content)
        pdf_reader = PdfReader(pdf_file)
        
        text = []
        for page in pdf_reader.pages:
            page_text = page.extract_text()
            if page_text:
                text.append(page_text)
        
        extracted_text = "\n".join(text)
        
        if not extracted_text.strip():
            raise FileProcessingError("No text could be extracted from PDF")
        
        app_logger.info(f"Extracted {len(extracted_text)} characters from PDF")
        return extracted_text
        
    except Exception as e:
        app_logger.error(f"PDF extraction failed: {str(e)}")
        raise FileProcessingError(f"Failed to extract text from PDF: {str(e)}")


def extract_text_from_docx(file_content: bytes) -> str:
    """
    Extract text from DOCX file.
    
    Args:
        file_content: DOCX file content as bytes
        
    Returns:
        Extracted text as string
        
    Raises:
        FileProcessingError: If DOCX processing fails
    """
    try:
        docx_file = io.BytesIO(file_content)
        doc = Document(docx_file)
        
        text = []
        for paragraph in doc.paragraphs:
            if paragraph.text.strip():
                text.append(paragraph.text)
        
        extracted_text = "\n".join(text)
        
        if not extracted_text.strip():
            raise FileProcessingError("No text could be extracted from DOCX")
        
        app_logger.info(f"Extracted {len(extracted_text)} characters from DOCX")
        return extracted_text
        
    except Exception as e:
        app_logger.error(f"DOCX extraction failed: {str(e)}")
        raise FileProcessingError(f"Failed to extract text from DOCX: {str(e)}")


def extract_text_from_url(url: str, timeout: int = None) -> str:
    """
    Extract text from web URL.
    
    Args:
        url: Web URL to fetch
        timeout: Request timeout in seconds (uses config default if not provided)
        
    Returns:
        Extracted text as string
        
    Raises:
        URLFetchError: If URL fetching or parsing fails
        SSLVerificationError: If SSL verification fails (when enabled)
    """
    if timeout is None:
        timeout = config.URL_FETCH_TIMEOUT
    
    try:
        # Fetch URL content
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(
            url,
            headers=headers,
            timeout=timeout,
            verify=config.VERIFY_SSL_CERTIFICATES
        )
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text
        text = soup.get_text()
        
        # Clean up text
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        if not text.strip():
            raise URLFetchError("No text could be extracted from URL")
        
        app_logger.info(f"Extracted {len(text)} characters from URL: {url}")
        return text
    
    except SSLError as e:
        # Only raise SSL error if verification is enabled
        if config.VERIFY_SSL_CERTIFICATES:
            app_logger.error(f"SSL verification failed for URL {url}: {str(e)}")
            raise SSLVerificationError(
                f"SSL certificate verification failed for {url}. "
                "The site may have a self-signed or invalid certificate."
            )
        else:
            # This shouldn't happen since we're bypassing verification
            app_logger.error(f"SSL error despite disabled verification for {url}: {str(e)}")
            raise URLFetchError(f"Failed to establish connection to {url}")
    except requests.Timeout:
        app_logger.error(f"Timeout while fetching URL: {url}")
        raise URLFetchError(f"The request timed out. The URL may be slow or unreachable.")
    except requests.RequestException as e:
        app_logger.error(f"URL fetch failed: {str(e)}")
        raise URLFetchError(f"Failed to fetch URL: {str(e)}")
    except Exception as e:
        app_logger.error(f"URL text extraction failed: {str(e)}")
        raise URLFetchError(f"Failed to extract text from URL: {str(e)}")


def extract_text(content: bytes, file_extension: str) -> str:
    """
    Extract text based on file extension.
    
    Args:
        content: File content as bytes
        file_extension: File extension (e.g., '.pdf', '.docx', '.txt')
        
    Returns:
        Extracted text as string
        
    Raises:
        UnsupportedFormatError: If file format is not supported
        FileProcessingError: If extraction fails
    """
    file_extension = file_extension.lower()
    
    if file_extension == '.pdf':
        return extract_text_from_pdf(content)
    elif file_extension == '.docx':
        return extract_text_from_docx(content)
    elif file_extension == '.txt':
        try:
            return content.decode('utf-8')
        except UnicodeDecodeError:
            raise FileProcessingError("Failed to decode text file (invalid UTF-8)")
    else:
        raise UnsupportedFormatError(f"Unsupported file format: {file_extension}")


def validate_file_size(file_size: int, max_size_mb: int) -> bool:
    """
    Validate file size.
    
    Args:
        file_size: File size in bytes
        max_size_mb: Maximum allowed size in MB
        
    Returns:
        True if valid
        
    Raises:
        FileSizeExceededError: If file size exceeds limit
    """
    from backend.app.errors import FileSizeExceededError
    
    max_size_bytes = max_size_mb * 1024 * 1024
    if file_size > max_size_bytes:
        raise FileSizeExceededError(
            f"File size ({file_size / 1024 / 1024:.2f}MB) exceeds maximum limit ({max_size_mb}MB)"
        )
    return True
