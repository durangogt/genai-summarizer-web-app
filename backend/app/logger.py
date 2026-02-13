"""Logging configuration using Loguru."""
import sys
from loguru import logger
from backend.app.config import config


def setup_logger():
    """Configure Loguru logger for the application."""
    # Remove default handler
    logger.remove()
    
    # Add console handler with custom format
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=config.LOG_LEVEL,
        colorize=True
    )
    
    # Add file handler for persistent logging
    logger.add(
        config.LOG_FILE,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level=config.LOG_LEVEL,
        rotation="10 MB",  # Rotate when file reaches 10MB
        retention="30 days",  # Keep logs for 30 days
        compression="zip"  # Compress rotated logs
    )
    
    logger.info("Logger initialized")
    return logger


# Initialize logger when module is imported
app_logger = setup_logger()


def log_audit_event(
    action: str,
    user_id: str,
    status: str,
    details: dict = None,
    error: str = None
):
    """
    Log an audit event with structured information.
    
    Args:
        action: The action being performed (e.g., 'batch_summarization', 'file_upload')
        user_id: Username or user identifier
        status: Status of the action ('started', 'success', 'failed')
        details: Additional details as a dictionary
        error: Error message if status is 'failed'
    """
    from datetime import datetime
    
    audit_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "user_id": user_id,
        "action": action,
        "status": status
    }
    
    if details:
        audit_data.update(details)
    
    if error:
        audit_data["error"] = error
    
    # Format as structured log entry
    log_message = f"AUDIT | {' | '.join(f'{k}={v}' for k, v in audit_data.items())}"
    
    if status == "failed":
        app_logger.error(log_message)
    elif status == "success":
        app_logger.info(log_message)
    else:
        app_logger.debug(log_message)
