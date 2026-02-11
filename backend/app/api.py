"""REST API endpoints for summarization service."""
from datetime import datetime, timedelta
from typing import Literal, Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, HttpUrl
from jose import JWTError, jwt
import os

from backend.app.config import config
from backend.app.logger import app_logger
from backend.app.errors import (
    FileProcessingError, 
    UnsupportedFormatError,
    FileSizeExceededError,
    AuthenticationError,
    InvalidRequestError
)
from backend.app.summarizer.utils import (
    extract_text, 
    extract_text_from_url,
    validate_file_size
)
from backend.app.summarizer.engine import summarizer_engine


# API Router
router = APIRouter(prefix="/api", tags=["api"])

# Security
security = HTTPBearer()

# In-memory storage for summaries (replace with database in production)
summary_history = []


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
        
        if not request.text.strip():
            raise InvalidRequestError("Text cannot be empty")
        
        summary = summarizer_engine.summarize(request.text, request.length)
        
        # Store in history
        history_entry = {
            "id": len(summary_history) + 1,
            "user": token_data.username,
            "type": "text",
            "length": request.length,
            "summary": summary,
            "timestamp": datetime.utcnow()
        }
        summary_history.append(history_entry)
        
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
            error=str(e)
        )


@router.post("/summarize/url", response_model=SummaryResponse)
async def summarize_url(
    request: SummarizeURLRequest,
    token_data: TokenData = Depends(verify_token)
):
    """Summarize content from URL."""
    try:
        app_logger.info(f"URL summarization requested by {token_data.username}: {request.url}")
        
        text = extract_text_from_url(str(request.url))
        summary = summarizer_engine.summarize(text, request.length)
        
        # Store in history
        history_entry = {
            "id": len(summary_history) + 1,
            "user": token_data.username,
            "type": "url",
            "source": str(request.url),
            "length": request.length,
            "summary": summary,
            "timestamp": datetime.utcnow()
        }
        summary_history.append(history_entry)
        
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
            error=str(e)
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
        
        # Read file content
        content = await file.read()
        
        # Validate file size
        validate_file_size(len(content), config.MAX_FILE_SIZE_MB)
        
        # Get file extension
        file_extension = os.path.splitext(file.filename)[1].lower()
        
        # Extract text
        text = extract_text(content, file_extension)
        
        # Generate summary
        summary = summarizer_engine.summarize(text, length)
        
        # Store in history
        history_entry = {
            "id": len(summary_history) + 1,
            "user": token_data.username,
            "type": "file",
            "source": file.filename,
            "length": length,
            "summary": summary,
            "timestamp": datetime.utcnow()
        }
        summary_history.append(history_entry)
        
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
            error=str(e)
        )


@router.post("/summarize/batch", response_model=BatchSummaryResponse)
async def summarize_batch(
    files: list[UploadFile] = File(...),
    length: Literal["short", "medium", "long"] = Form("medium"),
    token_data: TokenData = Depends(verify_token)
):
    """Batch summarize multiple files."""
    try:
        app_logger.info(f"Batch summarization requested by {token_data.username}: {len(files)} files")
        
        # Validate batch size
        if len(files) > config.MAX_BATCH_FILES:
            raise InvalidRequestError(f"Maximum {config.MAX_BATCH_FILES} files allowed per batch")
        
        results = []
        successful = 0
        failed = 0
        
        for idx, file in enumerate(files):
            try:
                content = await file.read()
                validate_file_size(len(content), config.MAX_FILE_SIZE_MB)
                
                file_extension = os.path.splitext(file.filename)[1].lower()
                text = extract_text(content, file_extension)
                summary = summarizer_engine.summarize(text, length)
                
                results.append({
                    "index": idx,
                    "filename": file.filename,
                    "success": True,
                    "summary": summary,
                    "error": None
                })
                successful += 1
                
            except Exception as e:
                results.append({
                    "index": idx,
                    "filename": file.filename,
                    "success": False,
                    "summary": None,
                    "error": str(e)
                })
                failed += 1
                app_logger.error(f"Batch file {file.filename} failed: {str(e)}")
        
        return BatchSummaryResponse(
            success=True,
            results=results,
            total=len(files),
            successful=successful,
            failed=failed
        )
        
    except Exception as e:
        app_logger.error(f"Batch summarization failed: {str(e)}")
        raise


@router.get("/history")
async def get_history(
    limit: int = 10,
    token_data: TokenData = Depends(verify_token)
):
    """Get summarization history for current user."""
    user_history = [
        entry for entry in summary_history 
        if entry["user"] == token_data.username
    ]
    
    # Return most recent entries
    recent_history = sorted(user_history, key=lambda x: x["timestamp"], reverse=True)[:limit]
    
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
