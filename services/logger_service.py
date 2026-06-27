"""
Logging service for FocusLens.
"""

import logging
import logging.handlers
from pathlib import Path
from config import Config


class LoggerService:
    """Centralized logging service."""

    _logger = None

    @classmethod
    def initialize(cls):
        """Initialize logger."""
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        logger = logging.getLogger("focuslens")
        logger.setLevel(Config.LOG_LEVEL)

        # File handler
        file_handler = logging.handlers.RotatingFileHandler(
            log_dir / Config.LOG_FILE,
            maxBytes=5 * 1024 * 1024,  # 5MB
            backupCount=5,
        )
        file_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
        )
        logger.addHandler(file_handler)

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(
            logging.Formatter("%(levelname)s - %(message)s")
        )
        logger.addHandler(console_handler)

        cls._logger = logger

    @classmethod
    def get_logger(cls, name: str = "focuslens") -> logging.Logger:
        """Get logger instance."""
        if cls._logger is None:
            cls.initialize()
        return logging.getLogger(name)

    @classmethod
    def info(cls, message: str):
        """Log info message."""
        cls.get_logger().info(message)

    @classmethod
    def debug(cls, message: str):
        """Log debug message."""
        cls.get_logger().debug(message)

    @classmethod
    def warning(cls, message: str):
        """Log warning message."""
        cls.get_logger().warning(message)

    @classmethod
    def error(cls, message: str):
        """Log error message."""
        cls.get_logger().error(message)

    @classmethod
    def critical(cls, message: str):
        """Log critical message."""
        cls.get_logger().critical(message)
