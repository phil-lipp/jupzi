from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import logging

from app.core.config import Config

logger = logging.getLogger(__name__)

class BaseService(ABC):
    """
    Base class for all services in the application.
    Provides common functionality and interface for all services.
    """
    def __init__(self, config: Config):
        """
        Initialize the base service.
        
        Args:
            config: Configuration object
        """
        self.config = config
        self._is_initialized = False

    @abstractmethod
    def initialize(self) -> None:
        """
        Initialize the service.
        Must be implemented by all service classes.
        """
        pass

    @abstractmethod
    def cleanup(self) -> None:
        """
        Clean up resources used by the service.
        Must be implemented by all service classes.
        """
        pass

    def is_initialized(self) -> bool:
        """Check if the service has been initialized."""
        return self._is_initialized

    def get_config(self) -> Config:
        """Get the service's configuration."""
        return self.config

    def get_config_value(self, key: str, default: Any = None) -> Any:
        """
        Get a configuration value.
        
        Args:
            key: Configuration key to retrieve
            default: Default value if key doesn't exist
            
        Returns:
            The configuration value or default if not found
        """
        return getattr(self.config, key, default)

    def log_error(self, message: str, error: Optional[Exception] = None) -> None:
        """
        Log an error message.
        
        Args:
            message: Error message to log
            error: Optional exception that caused the error
        """
        if error:
            logger.error(f"{message}: {str(error)}")
        else:
            logger.error(message)

    def log_info(self, message: str) -> None:
        """
        Log an info message.
        
        Args:
            message: Info message to log
        """
        logger.info(message)

    def log_debug(self, message: str) -> None:
        """
        Log a debug message.
        
        Args:
            message: Debug message to log
        """
        logger.debug(message) 