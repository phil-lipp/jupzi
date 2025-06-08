import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

from app.core.config import Config
from app.models.jobs import Job

logger = logging.getLogger(__name__)

class StateManager:
    """
    Manages the persistence and restoration of bot state.
    """
    def __init__(self, config: Config):
        """
        Initialize the state manager.
        
        Args:
            config: Configuration object containing state storage settings
        """
        self.config = config
        self.state_file = Path(config.state_file_path)
        self._current_state: Dict[str, Any] = {}
        self._last_save_time: Optional[datetime] = None

    def load_state(self) -> None:
        """Load the bot's state from persistent storage."""
        try:
            if not self.state_file.exists():
                logger.info("No existing state file found. Starting with empty state.")
                self._current_state = {}
                return

            with open(self.state_file, 'r') as f:
                self._current_state = json.load(f)
            
            logger.info("Successfully loaded state from storage")
        except Exception as e:
            logger.error(f"Failed to load state: {str(e)}")
            self._current_state = {}
            raise

    def save_state(self) -> None:
        """Save the current bot state to persistent storage."""
        try:
            # Ensure the directory exists
            self.state_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.state_file, 'w') as f:
                json.dump(self._current_state, f, indent=2)
            
            self._last_save_time = datetime.utcnow()
            logger.info("Successfully saved state to storage")
        except Exception as e:
            logger.error(f"Failed to save state: {str(e)}")
            raise

    def get_state(self, key: str, default: Any = None) -> Any:
        """
        Get a value from the current state.
        
        Args:
            key: The state key to retrieve
            default: Default value if key doesn't exist
            
        Returns:
            The state value or default if not found
        """
        return self._current_state.get(key, default)

    def set_state(self, key: str, value: Any) -> None:
        """
        Set a value in the current state.
        
        Args:
            key: The state key to set
            value: The value to store
        """
        self._current_state[key] = value

    def remove_state(self, key: str) -> None:
        """
        Remove a value from the current state.
        
        Args:
            key: The state key to remove
        """
        self._current_state.pop(key, None)

    def get_last_save_time(self) -> Optional[datetime]:
        """Get the timestamp of the last successful state save."""
        return self._last_save_time

    def clear_state(self) -> None:
        """Clear all state data."""
        self._current_state = {}
        if self.state_file.exists():
            self.state_file.unlink()
        logger.info("State cleared") 