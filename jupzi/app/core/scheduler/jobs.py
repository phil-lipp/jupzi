from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import logging

from app.core.base_service import BaseService
from app.core.config import Config
from app.models.jobs import Job
from app.services.calendar import CalendarService
from app.services.poll import PollService
from app.services.telegram import TelegramService

logger = logging.getLogger(__name__)

class WeeklyPollJob:
    """Job for creating and managing weekly polls."""
    
    def __init__(self, poll_service: PollService, telegram_service: TelegramService):
        self.poll_service = poll_service
        self.telegram_service = telegram_service
        self._current_poll: Optional[Dict[str, Any]] = None

    async def execute(self) -> None:
        """Execute the weekly poll job."""
        try:
            # Create new poll
            next_monday = self._get_next_monday()
            poll = self.poll_service.create_poll(
                title=f"Meeting Poll for {next_monday}",
                options=["Yes", "No", "Maybe"],
                creator_id=self.telegram_service.config.admin_chat_id
            )
            
            # Send poll to Telegram
            await self.telegram_service.send_poll(poll)
            
            # Store current poll info
            self._current_poll = {
                'id': poll.id,
                'message_id': poll.message_id,
                'created_at': datetime.utcnow()
            }
            
            logger.info(f"Weekly poll created for {next_monday}")
        except Exception as e:
            logger.error(f"Failed to execute weekly poll job: {str(e)}")
            raise

    def _get_next_monday(self) -> str:
        """Calculate the date of the next Monday."""
        today = datetime.now()
        days_until_monday = (7 - today.weekday()) % 7
        if days_until_monday == 0:  # If today is Monday
            days_until_monday = 7
        next_monday = today + timedelta(days=days_until_monday)
        return next_monday.strftime("%d.%m.")

class WeeklyOverviewJob:
    """Job for generating and sending weekly overview."""
    
    def __init__(self, calendar_service: CalendarService, telegram_service: TelegramService):
        self.calendar_service = calendar_service
        self.telegram_service = telegram_service

    async def execute(self) -> None:
        """Execute the weekly overview job."""
        try:
            # Generate overview
            overview = self.calendar_service.generate_week_overview()
            
            # Send to Telegram
            await self.telegram_service.send_message(overview)
            
            logger.info("Weekly overview sent successfully")
        except Exception as e:
            logger.error(f"Failed to execute weekly overview job: {str(e)}")
            raise

class FreeDatesJob:
    """Job for finding and reporting free dates."""
    
    def __init__(self, calendar_service: CalendarService, telegram_service: TelegramService):
        self.calendar_service = calendar_service
        self.telegram_service = telegram_service

    async def execute(self) -> None:
        """Execute the free dates job."""
        try:
            # Get free dates
            free_dates = self.calendar_service.get_free_dates()
            
            # Send to Telegram
            await self.telegram_service.send_message(free_dates)
            
            logger.info("Free dates report sent successfully")
        except Exception as e:
            logger.error(f"Failed to execute free dates job: {str(e)}")
            raise 