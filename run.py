"""CLI to start the GenAI Summarizer Web App."""
import os
import sys
import uvicorn
from backend.app.config import config
from backend.app.logger import app_logger


def main():
    """Start the web application."""
    try:
        # Log startup information
        app_logger.info("=" * 60)
        app_logger.info("GenAI Summarizer Web App")
        app_logger.info("=" * 60)
        app_logger.info(f"Host: {config.HOST}")
        app_logger.info(f"Port: {config.PORT}")
        app_logger.info(f"Log Level: {config.LOG_LEVEL}")
        app_logger.info("=" * 60)
        
        # Validate configuration before starting
        try:
            config.validate()
            app_logger.info("✓ Configuration validated")
        except ValueError as e:
            app_logger.error(f"✗ Configuration error: {str(e)}")
            app_logger.error("Please set required environment variables:")
            app_logger.error("  - GITHUB_TOKEN")
            app_logger.error("  - GITHUB_MODELS_ENDPOINT")
            sys.exit(1)
        
        # Start the server
        app_logger.info(f"Starting server at http://{config.HOST}:{config.PORT}")
        app_logger.info("Press CTRL+C to stop the server")
        
        uvicorn.run(
            "backend.app.main:app",
            host=config.HOST,
            port=config.PORT,
            reload=True,
            log_level=config.LOG_LEVEL.lower()
        )
        
    except KeyboardInterrupt:
        app_logger.info("\nShutdown requested by user")
        sys.exit(0)
    except Exception as e:
        app_logger.error(f"Failed to start server: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
