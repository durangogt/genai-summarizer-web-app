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
    app_logger.info(f"Starting PDF text extraction: file_size={len(file_content)} bytes")
    
    try:
        pdf_file = io.BytesIO(file_content)
        pdf_reader = PdfReader(pdf_file)
        
        page_texts = []
        for page_num, page in enumerate(pdf_reader.pages, start=1):
            extracted_page_text = page.extract_text()
            if extracted_page_text:
                page_texts.append(extracted_page_text)
                app_logger.debug(f"Extracted {len(extracted_page_text)} chars from page {page_num}")
        
        extracted_text = "\n".join(page_texts)
        
        if not extracted_text.strip():
            raise FileProcessingError("No text could be extracted from PDF")
        
        app_logger.info(f"PDF extraction completed: {len(extracted_text)} chars from {len(page_texts)} pages")
        return extracted_text
        
    except FileProcessingError:
        raise
    except Exception as pdf_error:
        app_logger.error(f"PDF extraction failed: {str(pdf_error)}")
        raise FileProcessingError(f"Failed to extract text from PDF: {str(pdf_error)}")


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
    app_logger.info(f"Starting DOCX text extraction: file_size={len(file_content)} bytes")
    
    try:
        docx_file = io.BytesIO(file_content)
        docx_document = Document(docx_file)
        
        paragraph_texts = []
        for para in docx_document.paragraphs:
            if para.text.strip():
                paragraph_texts.append(para.text)
        
        extracted_text = "\n".join(paragraph_texts)
        
        if not extracted_text.strip():
            raise FileProcessingError("No text could be extracted from DOCX")
        
        app_logger.info(f"DOCX extraction completed: {len(extracted_text)} chars from {len(paragraph_texts)} paragraphs")
        return extracted_text
        
    except FileProcessingError:
        raise
    except Exception as docx_error:
        app_logger.error(f"DOCX extraction failed: {str(docx_error)}")
        raise FileProcessingError(f"Failed to extract text from DOCX: {str(docx_error)}")


def _clean_html_text(raw_text: str) -> str:
    """Clean and normalize text extracted from HTML.
    
    Removes extra whitespace, collapses multiple spaces, and joins lines cleanly.
    
    Args:
        raw_text: Raw text extracted from HTML
        
    Returns:
        Cleaned and normalized text
    """
    lines = (line.strip() for line in raw_text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    return '\n'.join(chunk for chunk in chunks if chunk)


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
    
    app_logger.info(f"Starting URL text extraction: url={url}, timeout={timeout}s")
    
    try:
        # Fetch URL content
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        app_logger.debug(f"Fetching URL: {url}")
        response = requests.get(
            url,
            headers=headers,
            timeout=timeout,
            verify=config.VERIFY_SSL_CERTIFICATES
        )
        response.raise_for_status()
        app_logger.debug(f"URL fetched successfully: status_code={response.status_code}")
        
        # Parse HTML
        html_parser = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for unwanted_element in html_parser(["script", "style"]):
            unwanted_element.decompose()
        
        # Get text
        raw_text = html_parser.get_text()
        
        # Clean up text
        cleaned_text = _clean_html_text(raw_text)
        
        if not cleaned_text.strip():
            raise URLFetchError("No text could be extracted from URL")
        
        app_logger.info(f"URL extraction completed: {len(cleaned_text)} chars extracted from {url}")
        return cleaned_text
    
    except SSLError as ssl_error:
        # Only raise SSL error if verification is enabled
        if config.VERIFY_SSL_CERTIFICATES:
            app_logger.error(f"SSL verification failed for URL {url}: {str(ssl_error)}")
            raise SSLVerificationError(
                f"SSL certificate verification failed for {url}. "
                "The site may have a self-signed or invalid certificate."
            )
        else:
            # This shouldn't happen since we're bypassing verification
            app_logger.error(f"SSL error despite disabled verification for {url}: {str(ssl_error)}")
            raise URLFetchError(f"Failed to establish connection to {url}")
    except requests.Timeout as timeout_error:
        app_logger.error(f"Timeout while fetching URL: {url}")
        raise URLFetchError(f"The request timed out. The URL may be slow or unreachable.")
    except requests.RequestException as request_error:
        app_logger.error(f"URL fetch failed: {str(request_error)}")
        raise URLFetchError(f"Failed to fetch URL: {str(request_error)}")
    except Exception as unexpected_error:
        app_logger.error(f"URL text extraction failed: {str(unexpected_error)}")
        raise URLFetchError(f"Failed to extract text from URL: {str(unexpected_error)}")


def extract_text(file_content: bytes, file_extension: str) -> str:
    """
    Extract text based on file extension.
    
    Args:
        file_content: File content as bytes
        file_extension: File extension (e.g., '.pdf', '.docx', '.txt')
        
    Returns:
        Extracted text as string
        
    Raises:
        UnsupportedFormatError: If file format is not supported
        FileProcessingError: If extraction fails
    """
    normalized_extension = file_extension.lower()
    app_logger.info(f"Routing text extraction: extension={normalized_extension}")
    
    if normalized_extension == '.pdf':
        return extract_text_from_pdf(file_content)
    elif normalized_extension == '.docx':
        return extract_text_from_docx(file_content)
    elif normalized_extension == '.txt':
        try:
            decoded_text = file_content.decode('utf-8')
            app_logger.info(f"TXT extraction completed: {len(decoded_text)} chars")
            return decoded_text
        except UnicodeDecodeError as decode_error:
            app_logger.error(f"Failed to decode text file: {str(decode_error)}")
            raise FileProcessingError("Failed to decode text file (invalid UTF-8)")
    else:
        app_logger.error(f"Unsupported file format: {normalized_extension}")
        raise UnsupportedFormatError(f"Unsupported file format: {normalized_extension}")


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
