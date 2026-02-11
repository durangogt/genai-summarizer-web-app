# GitHub Copilot Instructions for GenAI Summarizer Web App

## Project Context

This is a Python-based document summarization application using Azure OpenAI. The entire stack (backend and frontend) is implemented in Python only, with Jinja2 templates for the web UI.

## Key Architecture Rules

### Directory Structure
Follow the directory structure defined in `architecture.md`:
- `backend/app/` - Core application logic
- `backend/app/summarizer/` - Summarization engine and utilities
- `frontend/templates/` - Jinja2 templates for UI
- `tests/` - Unit tests for all components

### Technology Stack
- **Backend**: FastAPI with Uvicorn
- **Frontend**: Python with Jinja2 templates (NO JavaScript frameworks)
- **AI Model**: Azure OpenAI (configured via environment variables)
- **File Processing**: PyPDF2 (PDF), python-docx (DOCX), BeautifulSoup4 (web URLs)
- **Authentication**: JWT tokens via python-jose
- **Logging**: Loguru

### Critical Development Guidelines

1. **Requirements.txt Management**
   - Always use the EXACT package list from `architecture.md`
   - Never add, remove, or modify packages without explicit request
   - When updating, copy the complete list as-is

2. **Server Configuration**
   - Default host: `127.0.0.1` for local development
   - Port: Read from `PORT` environment variable, fallback to 8000
   - Never use `0.0.0.0` unless explicitly requested for deployment

3. **Startup Script (startup.sh)**
   - Use the exact structure defined in `architecture.md`
   - Must upgrade pip, install requirements, and run the app
   - Include error handling with `set -e`
   - Print clear status messages

4. **Python-Only Implementation**
   - Both backend and frontend are Python-only
   - Use Jinja2 templates for all UI components
   - No React, Vue, or other JavaScript frameworks

5. **Configuration Management**
   - All secrets and configuration via environment variables
   - Load settings in `backend/app/config.py`
   - Never hardcode API keys or credentials

6. **Error Handling**
   - User-friendly error messages in both UI and API
   - Comprehensive logging via Loguru
   - Custom error classes in `backend/app/errors.py`

7. **File Size Limits**
   - Maximum upload size: 10MB per file
   - Batch processing: Up to 10 files per request

8. **Summary Length Options**
   - Support three modes: short, medium, long
   - Configurable via API parameter or UI selection

## Testing Requirements

- Write unit tests for all new features
- Test files location: `backend/tests/`
- Coverage includes: API endpoints, summarizer logic, authentication, history

## Common Tasks

### Adding a New Feature
1. Check `feature-request.md` for feature specifications
2. Update relevant files in `backend/app/`
3. Add corresponding tests
4. Update logging for audit trail

### Modifying API Endpoints
1. Edit `backend/app/api.py`
2. Ensure JWT authentication is maintained
3. Add comprehensive error handling
4. Update tests in `tests/test_api.py`

### Updating Summarization Logic
1. Modify `backend/app/summarizer/engine.py`
2. Ensure configurable length is respected
3. Test with various input formats
4. Update `tests/test_summarizer.py`

## Environment Variables

Required environment variables:
- `AZURE_OPENAI_API_KEY` - Azure OpenAI API key
- `AZURE_OPENAI_ENDPOINT` - Azure OpenAI endpoint URL
- `PORT` - Server port (optional, defaults to 8000)
- `SECRET_KEY` - JWT token secret key

## Deployment Considerations

- Self-hosted on Windows or Linux servers
- Scales horizontally for large document sets
- Use `startup.sh` for automated deployment
- Review `requirements.md` for deployment checklist

## Reference Documentation

Always consult these files before making changes:
- `architecture.md` - Directory structure and file purposes
- `requirements.md` - Functional and non-functional requirements
- `feature-request.md` - Feature specifications and user stories

## Accessibility Requirements

- Web UI must support keyboard navigation
- Screen reader compatibility required
- Responsive design for various screen sizes
- Clear notifications via popups for completion/errors
