"""Web UI backend logic using FastAPI and Jinja2 templates."""
from datetime import datetime
from fastapi import APIRouter, Request, Form, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from backend.app.logger import app_logger
from backend.app.config import config
from backend.app.errors import get_user_friendly_message
from backend.app.summarizer.service import summarizer_service


# UI Router
router = APIRouter(tags=["ui"])

# Setup Jinja2 templates
templates = Jinja2Templates(directory="frontend/templates")


@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Render dashboard/home page."""
    app_logger.info("Dashboard accessed")
    return templates.TemplateResponse("index.html", {
        "request": request,
        "title": "GenAI Summarizer"
    })


@router.get("/upload", response_class=HTMLResponse)
async def upload_page(request: Request):
    """Render file upload page."""
    app_logger.info("Upload page accessed")
    return templates.TemplateResponse("upload.html", {
        "request": request,
        "title": "Upload Document",
        "max_file_size": config.MAX_FILE_SIZE_MB,
        "allowed_extensions": ", ".join(config.ALLOWED_EXTENSIONS)
    })


@router.post("/upload", response_class=HTMLResponse)
async def process_upload(
    request: Request,
    file: UploadFile = File(...),
    length: str = Form("medium")
):
    """Process file upload and generate summary."""
    try:
        app_logger.info(f"Processing upload: {file.filename}")
        
        content = await file.read()
        summary = summarizer_service.summarize_file(content, file.filename, length)
        summarizer_service.add_ui_history(
            source_type="file",
            length=length,
            summary=summary,
            source=file.filename,
        )
        
        app_logger.info(f"Upload processed successfully: {file.filename}")
        
        return templates.TemplateResponse("result.html", {
            "request": request,
            "title": "Summary Result",
            "success": True,
            "summary": summary,
            "source": file.filename,
            "source_type": "file",
            "length": length,
            "timestamp": datetime.utcnow()
        })
        
    except Exception as e:
        app_logger.error(f"Upload processing failed: {str(e)}")
        return templates.TemplateResponse("result.html", {
            "request": request,
            "title": "Summary Result",
            "success": False,
            "error": get_user_friendly_message(e),
            "source": file.filename if file else "unknown",
            "timestamp": datetime.utcnow()
        })


@router.get("/text", response_class=HTMLResponse)
async def text_page(request: Request):
    """Render text input page."""
    app_logger.info("Text input page accessed")
    return templates.TemplateResponse("text.html", {
        "request": request,
        "title": "Summarize Text"
    })


@router.post("/text", response_class=HTMLResponse)
async def process_text(
    request: Request,
    text: str = Form(...),
    length: str = Form("medium")
):
    """Process text input and generate summary."""
    try:
        app_logger.info("Processing text input")
        
        summary = summarizer_service.summarize_text(text, length)
        summarizer_service.add_ui_history(
            source_type="text",
            length=length,
            summary=summary,
        )
        
        app_logger.info("Text processed successfully")
        
        return templates.TemplateResponse("result.html", {
            "request": request,
            "title": "Summary Result",
            "success": True,
            "summary": summary,
            "source": "Direct Text Input",
            "source_type": "text",
            "length": length,
            "timestamp": datetime.utcnow()
        })
        
    except Exception as e:
        app_logger.error(f"Text processing failed: {str(e)}")
        return templates.TemplateResponse("result.html", {
            "request": request,
            "title": "Summary Result",
            "success": False,
            "error": get_user_friendly_message(e),
            "source": "Direct Text Input",
            "timestamp": datetime.utcnow()
        })


@router.get("/url", response_class=HTMLResponse)
async def url_page(request: Request):
    """Render URL input page."""
    app_logger.info("URL input page accessed")
    return templates.TemplateResponse("url.html", {
        "request": request,
        "title": "Summarize URL"
    })


@router.post("/url", response_class=HTMLResponse)
async def process_url(
    request: Request,
    url: str = Form(...),
    length: str = Form("medium")
):
    """Process URL and generate summary."""
    try:
        app_logger.info(f"Processing URL: {url}")
        
        summary = summarizer_service.summarize_url(url, length)
        summarizer_service.add_ui_history(
            source_type="url",
            length=length,
            summary=summary,
            source=url,
        )
        
        app_logger.info(f"URL processed successfully: {url}")
        
        return templates.TemplateResponse("result.html", {
            "request": request,
            "title": "Summary Result",
            "success": True,
            "summary": summary,
            "source": url,
            "source_type": "url",
            "length": length,
            "timestamp": datetime.utcnow()
        })
        
    except Exception as e:
        app_logger.error(f"URL processing failed: {str(e)}")
        return templates.TemplateResponse("result.html", {
            "request": request,
            "title": "Summary Result",
            "success": False,
            "error": get_user_friendly_message(e),
            "source": url if url else "unknown",
            "timestamp": datetime.utcnow()
        })


@router.get("/history", response_class=HTMLResponse)
async def history_page(request: Request):
    """Render history page."""
    app_logger.info("History page accessed")
    
    recent_history = summarizer_service.get_ui_history()
    
    return templates.TemplateResponse("history.html", {
        "request": request,
        "title": "Summary History",
        "history": recent_history,
        "count": len(recent_history)
    })


@router.get("/batch", response_class=HTMLResponse)
async def batch_page(request: Request):
    """Render batch upload page."""
    app_logger.info("Batch upload page accessed")
    return templates.TemplateResponse("batch.html", {
        "request": request,
        "title": "Batch Processing",
        "max_files": config.MAX_BATCH_FILES,
        "max_file_size": config.MAX_FILE_SIZE_MB
    })


@router.post("/batch", response_class=HTMLResponse)
async def process_batch(
    request: Request,
    files: list[UploadFile] = File(...),
    length: str = Form("medium")
):
    """Process batch file upload and generate summaries."""
    try:
        app_logger.info(f"Processing batch upload: {len(files)} files")
        
        if len(files) > config.MAX_BATCH_FILES:
            raise ValueError(f"Maximum {config.MAX_BATCH_FILES} files allowed")
        
        results = []
        
        for file in files:
            try:
                content = await file.read()
                summary = summarizer_service.summarize_file(content, file.filename, length)
                
                results.append({
                    "filename": file.filename,
                    "success": True,
                    "summary": summary,
                    "error": None
                })
                
            except Exception as e:
                results.append({
                    "filename": file.filename,
                    "success": False,
                    "summary": None,
                    "error": str(e)
                })
                app_logger.error(f"Batch file {file.filename} failed: {str(e)}")
        
        app_logger.info(f"Batch processing completed: {len(results)} files")
        
        return templates.TemplateResponse("batch_result.html", {
            "request": request,
            "title": "Batch Summary Results",
            "results": results,
            "total": len(results),
            "successful": sum(1 for r in results if r["success"]),
            "failed": sum(1 for r in results if not r["success"]),
            "length": length,
            "timestamp": datetime.utcnow()
        })
        
    except Exception as e:
        app_logger.error(f"Batch processing failed: {str(e)}")
        return templates.TemplateResponse("batch_result.html", {
            "request": request,
            "title": "Batch Summary Results",
            "results": [],
            "total": 0,
            "successful": 0,
            "failed": 0,
            "error": get_user_friendly_message(e),
            "timestamp": datetime.utcnow()
        })
