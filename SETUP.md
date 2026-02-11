# Setup Instructions for GenAI Summarizer Web App

## Quick Start Guide

### 1. Python Virtual Environment

A Python virtual environment has already been created at `.venv/`.

**To activate it:**

Windows (PowerShell):
```powershell
.\.venv\Scripts\Activate.ps1
```

Windows (CMD):
```cmd
.venv\Scripts\activate.bat
```

Linux/Mac:
```bash
source .venv/bin/activate
```

### 2. Install Dependencies

The installation was interrupted. Please complete it by running:

```powershell
# Make sure virtual environment is activated
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Copy the `.env.template` file to `.env` and fill in your Azure OpenAI credentials:

```powershell
Copy-Item .env.template .env
```

Then edit `.env` and add your actual values:

```
AZURE_OPENAI_API_KEY=your-actual-api-key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=your-deployment-name
```

### 4. Run the Application

Once dependencies are installed and `.env` is configured:

```powershell
python run.py
```

The application will start at: [http://127.0.0.1:8000](http://127.0.0.1:8000)

### 5. Access the Web Interface

Open your browser and navigate to:
- **Home/Dashboard:** http://127.0.0.1:8000/
- **API Documentation:** http://127.0.0.1:8000/docs
- **Health Check:** http://127.0.0.1:8000/health

### 6. Run Tests

To run the test suite:

```powershell
pytest backend/tests/ -v
```

For coverage report:

```powershell
pytest backend/tests/ --cov=backend/app --cov-report=html
```

## Project Structure

```
genai-summarizer-web-app/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py          # Application entry point
│   │   ├── api.py           # REST API endpoints
│   │   ├── ui.py            # Web UI routes
│   │   ├── config.py        # Configuration management
│   │   ├── logger.py        # Logging setup
│   │   ├── errors.py        # Error handling
│   │   └── summarizer/
│   │       ├── __init__.py
│   │       ├── engine.py    # Summarization logic
│   │       └── utils.py     # Text extraction utilities
│   └── tests/
│       ├── __init__.py
│       ├── test_api.py
│       ├── test_summarizer.py
│       ├── test_auth.py
│       └── test_history.py
├── frontend/
│   ├── __init__.py
│   └── templates/           # Jinja2 HTML templates
│       ├── base.html
│       ├── index.html
│       ├── text.html
│       ├── upload.html
│       ├── url.html
│       ├── batch.html
│       ├── result.html
│       ├── batch_result.html
│       └── history.html
├── .venv/                   # Virtual environment (already created)
├── requirements.txt         # Python dependencies
├── run.py                   # Application runner
├── startup.sh              # Startup script for deployment
├── .env.template           # Environment variables template
├── README.md               # Project documentation
└── .gitignore             # Git ignore rules
```

## Features Implemented

✅ **Multi-format Input Support**
- Plain text input
- PDF file upload
- DOCX file upload
- Web URL summarization

✅ **Configurable Summary Lengths**
- Short (1-2 sentences)
- Medium (2-4 sentences)
- Long (4-8 sentences)

✅ **REST API**
- JWT authentication
- Text, file, and URL endpoints
- Batch processing
- History tracking

✅ **Web UI**
- Responsive design
- Keyboard navigation support
- File upload interface
- History viewing
- Batch processing

✅ **Error Handling & Logging**
- Custom error classes
- User-friendly error messages
- Comprehensive audit logging
- Loguru integration

✅ **Testing**
- Unit tests for API endpoints
- Summarizer logic tests
- Authentication tests
- History tracking tests

## Next Steps

1. **Complete dependency installation** (if interrupted)
2. **Configure Azure OpenAI credentials** in `.env`
3. **Run the application** with `python run.py`
4. **Test the features** through the web interface
5. **Run the test suite** to verify everything works

## Troubleshooting

### Import Errors

If you see import errors, make sure:
1. Virtual environment is activated
2. All dependencies are installed
3. You're running commands from the project root

### Configuration Errors

If you see configuration validation errors:
1. Check that `.env` file exists (not `.env.template`)
2. Verify Azure OpenAI credentials are correct
3. Ensure no extra spaces in environment variable values

### Port Already in Use

If port 8000 is already in use, change it in `.env`:
```
PORT=8080
```

## Documentation

For detailed information, refer to:
- [README.md](README.md) - Project overview
- [architecture.md](architecture.md) - System architecture
- [requirements.md](requirements.md) - Requirements specification
- [feature-request.md](feature-request.md) - Feature details

## Lab Guide

For complete deployment instructions, see the [CloudLabs Lab Guide](https://experience.cloudlabs.ai/#/labguidepreview/802a9f23-0da5-4afd-a471-e53fc491b5b4/1).
