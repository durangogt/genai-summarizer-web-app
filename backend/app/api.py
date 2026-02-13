"""REST API endpoints for summarization service."""
from datetime import datetime, timedelta
from typing import Literal, Optional
from fastapi import APIRouter, UploadFile, File, Form, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, HttpUrl
from jose import JWTError, jwt

from backend.app.config import config
from backend.app.logger import app_logger
from backend.app.errors import (
    AuthenticationError,
    InvalidRequestError,
    SummarizerException,
    get_user_friendly_message,
)
from backend.app.summarizer.service import summarizer_service


# API Router
router = APIRouter(prefix="/api", tags=["api"])

# Security
security = HTTPBearer()


# Pydantic Models
class TokenData(BaseModel):
    """JWT token data."""
    username: str
    exp: Optional[datetime] = None


class SummarizeTextRequest(BaseModel):
    """Request model for text summarization."""
    text: str
    length: Literal["short", "medium", "long"] = "medium"


class SummarizeURLRequest(BaseModel):
    """Request model for URL summarization."""
    url: HttpUrl
    length: Literal["short", "medium", "long"] = "medium"


class SummaryResponse(BaseModel):
    """Response model for summarization."""
    success: bool
    summary: Optional[str] = None
    length: str
    timestamp: datetime
    error: Optional[str] = None


class BatchSummaryResponse(BaseModel):
    """Response model for batch summarization."""
    success: bool
    results: list[dict]
    total: int
    successful: int
    failed: int


# Authentication Functions
def create_access_token(data: dict) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)
    return encoded_jwt


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)) -> TokenData:
    """Verify JWT token."""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise AuthenticationError("Invalid token")
        return TokenData(username=username)
    except JWTError:
        raise AuthenticationError("Invalid or expired token")


# API Endpoints
@router.post("/token")
async def login(username: str = Form(...), password: str = Form(...)):
    """
    Generate JWT token for authentication.
    Note: This is a simplified example. Use proper user authentication in production.
    """
    # Simplified authentication (replace with proper user validation)
    if username and password:
        access_token = create_access_token(data={"sub": username})
        app_logger.info(f"Token generated for user: {username}")
        return {"access_token": access_token, "token_type": "bearer"}
    raise AuthenticationError("Invalid credentials")


@router.post("/summarize/text", response_model=SummaryResponse)
async def summarize_text(
    request: SummarizeTextRequest,
    token_data: TokenData = Depends(verify_token)
):
    """Summarize plain text."""
    try:
        app_logger.info(f"Text summarization requested by {token_data.username} (length: {request.length})")
        
        summary = summarizer_service.summarize_text(request.text, request.length)
        summarizer_service.add_api_history(
            user=token_data.username,
            source_type="text",
            length=request.length,
            summary=summary,
        )
        
        return SummaryResponse(
            success=True,
            summary=summary,
            length=request.length,
            timestamp=datetime.utcnow()
        )
    except Exception as e:
        app_logger.error(f"Text summarization failed: {str(e)}")
        return SummaryResponse(
            success=False,
            summary=None,
            length=request.length,
            timestamp=datetime.utcnow(),
            error=get_user_friendly_message(e)
        )


@router.post("/summarize/url", response_model=SummaryResponse)
async def summarize_url(
    request: SummarizeURLRequest,
    token_data: TokenData = Depends(verify_token)
):
    """Summarize content from URL."""
    try:
        app_logger.info(f"URL summarization requested by {token_data.username}: {request.url}")
        
        summary = summarizer_service.summarize_url(str(request.url), request.length)
        summarizer_service.add_api_history(
            user=token_data.username,
            source_type="url",
            length=request.length,
            summary=summary,
            source=str(request.url),
        )
        
        return SummaryResponse(
            success=True,
            summary=summary,
            length=request.length,
            timestamp=datetime.utcnow()
        )
    except Exception as e:
        app_logger.error(f"URL summarization failed: {str(e)}")
        return SummaryResponse(
            success=False,
            summary=None,
            length=request.length,
            timestamp=datetime.utcnow(),
            error=get_user_friendly_message(e)
        )


@router.post("/summarize/file", response_model=SummaryResponse)
async def summarize_file(
    file: UploadFile = File(...),
    length: Literal["short", "medium", "long"] = Form("medium"),
    token_data: TokenData = Depends(verify_token)
):
    """Summarize uploaded file (PDF, DOCX, TXT)."""
    try:
        app_logger.info(f"File summarization requested by {token_data.username}: {file.filename}")
        
        content = await file.read()
        summary = summarizer_service.summarize_file(content, file.filename, length)
        summarizer_service.add_api_history(
            user=token_data.username,
            source_type="file",
            length=length,
            summary=summary,
            source=file.filename,
        )
        
        return SummaryResponse(
            success=True,
            summary=summary,
            length=length,
            timestamp=datetime.utcnow()
        )
    except Exception as e:
        app_logger.error(f"File summarization failed: {str(e)}")
        return SummaryResponse(
            success=False,
            summary=None,
            length=length,
            timestamp=datetime.utcnow(),
            error=get_user_friendly_message(e)
        )


@router.post("/summarize/batch", response_model=BatchSummaryResponse)
async def summarize_batch(
    files: list[UploadFile] = File(...),
    length: Literal["short", "medium", "long"] = Form("medium"),
    token_data: TokenData = Depends(verify_token)
):
    """Batch summarize multiple files."""
    from backend.app.logger import log_audit_event
    
    filenames = [f.filename for f in files]
    
    try:
        app_logger.info(
            f"Batch summarization requested by {token_data.username}: "
            f"{len(files)} files, length={length}"
        )
        
        # Log initial request
        log_audit_event(
            action="batch_request_received",
            user_id=token_data.username,
            status="started",
            details={
                "file_count": len(files),
                "summary_length": length,
                "filenames": filenames
            }
        )
        
        # Read all file contents first (async I/O)
        file_data = []
        for file in files:
            content = await file.read()
            file_data.append((content, file.filename))
            app_logger.debug(
                f"File read: user_id={token_data.username}, "
                f"filename={file.filename}, size={len(content)} bytes"
            )
        
        # Process batch with audit logging
        results = summarizer_service.summarize_batch(
            file_data, 
            length,
            user_id=token_data.username
        )
        successful = sum(1 for r in results if r["success"])
        failed = sum(1 for r in results if not r["success"])
        
        # Log successful batch completion
        log_audit_event(
            action="batch_request_completed",
            user_id=token_data.username,
            status="success",
            details={
                "total_files": len(files),
                "successful": successful,
                "failed": failed
            }
        )
        
        app_logger.info(
            f"Batch summarization completed for {token_data.username}: "
            f"{successful}/{len(files)} successful"
        )
        
        return BatchSummaryResponse(
            success=True,
            results=results,
            total=len(files),
            successful=successful,
            failed=failed
        )
        
    except Exception as e:
        error_msg = str(e)
        friendly_msg = get_user_friendly_message(e)
        
        # Log batch failure
        log_audit_event(
            action="batch_request_completed",
            user_id=token_data.username,
            status="failed",
            details={
                "file_count": len(files),
                "filenames": filenames
            },
            error=f"{error_msg} | User-friendly: {friendly_msg}"
        )
        
        app_logger.error(
            f"Batch summarization failed for {token_data.username}: {error_msg}"
        )
        raise


@router.get("/history")
async def get_history(
    limit: int = 10,
    token_data: TokenData = Depends(verify_token)
):
    """Get summarization history for current user."""
    recent_history = summarizer_service.get_api_history(token_data.username, limit)
    
    app_logger.info(f"History requested by {token_data.username}: {len(recent_history)} entries")
    
    return {
        "success": True,
        "count": len(recent_history),
        "history": recent_history
    }


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow()
    }
