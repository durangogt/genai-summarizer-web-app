# GenAI Summarizer Web App

A self-hosted Python application that generates concise summaries from text documents, PDFs, DOCX files, and web URLs using GitHub Models.

## Overview

This application provides both a REST API and a simple web interface for document summarization. Built entirely in Python, it offers configurable summary lengths, batch processing capabilities, and comprehensive logging.

## Key Features

- **Multi-format Input**: Supports plain text, PDF, DOCX, and web URLs
- **Configurable Summaries**: Choose between short, medium, or long summaries
- **REST API**: Integration-ready endpoints with JWT authentication
- **Web UI**: Responsive interface with upload forms and summary history
- **Batch Processing**: Process up to 10 files simultaneously
- **GitHub Models Integration**: Powered by GitHub Models AI

## Quick Start

1. Create and activate a Python virtual environment
2. Install dependencies: `pip install -r requirements.txt`
3. Configure environment variables for GitHub Models
4. Run the application: `python run.py`
5. Access the web UI at `http://127.0.0.1:8000`

## Requirements

- Python 3.8+
- GitHub token with access to Models API
- Maximum file size: 10MB per upload

## Lab Guide

For detailed setup and deployment instructions, refer to the [CloudLabs Lab Guide](https://experience.cloudlabs.ai/#/labguidepreview/802a9f23-0da5-4afd-a471-e53fc491b5b4/1).

## Documentation

### 📚 Online Documentation

Visit our comprehensive documentation site: **[https://durangogt.github.io/genai-summarizer-web-app/](https://durangogt.github.io/genai-summarizer-web-app/)**

The documentation includes:
- Complete setup and installation guide
- API reference with examples
- Usage tutorials and best practices
- Deployment instructions

### 📄 Project Documentation

See the following files for detailed information:
- [architecture.md](architecture.md) - Application structure and file organization
- [requirements.md](requirements.md) - Functional and non-functional requirements
- [feature-request.md](feature-request.md) - Feature specifications and user stories
- [GITHUB_PAGES_SETUP.md](GITHUB_PAGES_SETUP.md) - GitHub Pages deployment guide

## License

This project is provided as-is for educational and demonstration purposes.
