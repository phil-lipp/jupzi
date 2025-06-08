from typing import Dict, Optional
from datetime import datetime
import logging
from pathlib import Path

from app.core.persistence.state_manager import StateManager
from app.core.scheduler.scheduler import JobScheduler
from app.core.config import Config
from app.models.jobs import Job

logger = logging.getLogger(__name__)

class JupziBot:
    """
    Main bot class that orchestrates all bot operations and manages state.
    """
    def __init__(self, config: Config):
        """
        Initialize the bot with configuration and core components.
        
        Args:
            config: Configuration object containing bot settings
        """
        self.config = config
        self.state_manager = StateManager(config)
        self.scheduler = JobScheduler()
        self.services: Dict[str, object] = {}
        self._is_running = False
        self._start_time: Optional[datetime] = None

    def initialize_services(self) -> None:
        """Initialize all required services for the bot."""
        try:
            # Initialize core services
            from app.services.calendar import CalendarService
            from app.services.telegram import TelegramService
            from app.services.poll import PollService

            self.services['calendar'] = CalendarService(self.config)
            self.services['telegram'] = TelegramService(self.config)
            self.services['poll'] = PollService(self.config)
            
            logger.info("All services initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize services: {str(e)}")
            raise

    def start(self) -> None:
        """Start the bot and all its components."""
        try:
            logger.info("Starting JupziBot...")
            self._start_time = datetime.utcnow()
            self._is_running = True
            
            # Load previous state if exists
            self.state_manager.load_state()
            
            # Initialize and start services
            self.initialize_services()
            self.scheduler.start()
            
            logger.info("JupziBot started successfully")
        except Exception as e:
            logger.error(f"Failed to start bot: {str(e)}")
            self._is_running = False
            raise

    def stop(self) -> None:
        """Stop the bot and save its current state."""
        try:
            logger.info("Stopping JupziBot...")
            self._is_running = False
            
            # Stop scheduler and save state
            self.scheduler.stop()
            self.state_manager.save_state()
            
            logger.info("JupziBot stopped successfully")
        except Exception as e:
            logger.error(f"Error while stopping bot: {str(e)}")
            raise

    def is_running(self) -> bool:
        """Check if the bot is currently running."""
        return self._is_running

    def get_uptime(self) -> Optional[float]:
        """Get the bot's uptime in seconds."""
        if self._start_time is None:
            return None
        return (datetime.utcnow() - self._start_time).total_seconds()

    def get_service(self, service_name: str) -> object:
        """
        Get a service instance by name.
        
        Args:
            service_name: Name of the service to retrieve
            
        Returns:
            The requested service instance
            
        Raises:
            KeyError: If the service doesn't exist
        """
        if service_name not in self.services:
            raise KeyError(f"Service '{service_name}' not found")
        return self.services[service_name] 