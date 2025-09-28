# utils/logger_config.py
import logging
import sys
from typing import Optional

class AppLogger:
    """Centralized logger configuration for the entire application"""
    
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not AppLogger._initialized:
            self._setup_logging()
            AppLogger._initialized = True
    
    def _setup_logging(self):
        """Setup the main application logger"""
        # Main application logger
        self.logger = logging.getLogger("applogger")
        self.logger.setLevel(logging.DEBUG)
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "%(asctime)s | %(name)s:%(levelname)s | %(filename)s:%(lineno)d | %(message)s"
        )
        console_handler.setFormatter(formatter)
        
        # Add handler if not already added
        if not self.logger.handlers:
            self.logger.addHandler(console_handler)
        
        # Prevent duplicate logs
        self.logger.propagate = False
    
    def get_logger(self, module_name: Optional[str] = None) -> logging.Logger:
        """Get a logger for a specific module"""
        if module_name:
            # Create child logger for specific modules
            child_logger = self.logger.getChild(module_name)
            return child_logger
        return self.logger

# Global instance
app_logger = AppLogger()

# Easy import for other modules
def get_logger(module_name: Optional[str] = None) -> logging.Logger:
    """Get the application logger"""
    return app_logger.get_logger(module_name)

# Default logger for backwards compatibility
logger = app_logger.get_logger()
