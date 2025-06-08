from typing import List, Optional, Dict, Set
from datetime import datetime, timedelta
import logging

from app.core.base_service import BaseService
from app.core.config import Config
from app.models.calendar_events import CalendarEvent
from app.utils.calendar_utils import get_calendar_client, get_local_time, format_event, get_event_sort_key
from app.utils.templates import (
    WEEKDAY_TRANSLATIONS,
    FOOTER_TEXT,
    FREE_DAYS_HEADER,
    WEEKLY_OVERVIEW_HEADER
)

logger = logging.getLogger(__name__)

class CalendarService(BaseService):
    """
    Service for managing calendar events and notifications.
    """
    def __init__(self, config: Config):
        super().__init__(config)
        self._check_interval = self.get_config_value('calendar_check_interval', 300)
        self._events: List[CalendarEvent] = []
        self._calendar_client = None

    def initialize(self) -> None:
        """Initialize the calendar service."""
        try:
            self._calendar_client = get_calendar_client()
            if not self._calendar_client:
                raise RuntimeError("Failed to initialize calendar client")
                
            # Load existing events from database
            self._load_events()
            self._is_initialized = True
            self.log_info("Calendar service initialized")
        except Exception as e:
            self.log_error("Failed to initialize calendar service", e)
            raise

    def cleanup(self) -> None:
        """Clean up calendar service resources."""
        self._events.clear()
        self._calendar_client = None
        self._is_initialized = False
        self.log_info("Calendar service cleaned up")

    def _load_events(self) -> None:
        """Load events from the database."""
        # TODO: Implement database loading
        pass

    def get_upcoming_events(self, hours: int = 24) -> List[CalendarEvent]:
        """
        Get events scheduled within the next specified hours.
        
        Args:
            hours: Number of hours to look ahead
            
        Returns:
            List of upcoming calendar events
        """
        now = datetime.utcnow()
        end_time = now + timedelta(hours=hours)
        
        return [
            event for event in self._events
            if now <= event.start_time <= end_time
        ]

    def add_event(self, event: CalendarEvent) -> None:
        """
        Add a new calendar event.
        
        Args:
            event: Calendar event to add
        """
        try:
            # TODO: Save to database
            self._events.append(event)
            self.log_info(f"Added calendar event: {event.title}")
        except Exception as e:
            self.log_error(f"Failed to add calendar event: {event.title}", e)
            raise

    def remove_event(self, event_id: int) -> None:
        """
        Remove a calendar event.
        
        Args:
            event_id: ID of the event to remove
        """
        try:
            # TODO: Remove from database
            self._events = [e for e in self._events if e.id != event_id]
            self.log_info(f"Removed calendar event with ID: {event_id}")
        except Exception as e:
            self.log_error(f"Failed to remove calendar event: {event_id}", e)
            raise

    def get_event(self, event_id: int) -> Optional[CalendarEvent]:
        """
        Get a calendar event by ID.
        
        Args:
            event_id: ID of the event to retrieve
            
        Returns:
            Calendar event if found, None otherwise
        """
        try:
            return next((e for e in self._events if e.id == event_id), None)
        except Exception as e:
            self.log_error(f"Failed to get calendar event: {event_id}", e)
            return None

    def get_free_dates(self) -> str:
        """
        Generates a list of days without events in the next two weeks.
        
        Returns:
            str: Formatted message with all free days
        """
        if not self._calendar_client:
            return "Error connecting to the calendar."

        current_time = get_local_time()
        
        # Calculate start (today) and end (in 2 weeks)
        start_date = current_time.replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = start_date + timedelta(days=14, hours=23, minutes=59, seconds=59)
        
        # Create a list of all days in the period
        all_days = set()
        current_date = start_date
        while current_date <= end_date:
            all_days.add(current_date.date())
            current_date += timedelta(days=1)
        
        try:
            # Get all events in the period
            events = self._calendar_client.search(
                start=start_date,
                end=end_date,
                expand=True  # Expands recurring events
            )
            
            # Collect all days with events
            days_with_events = set()
            
            for event in events:
                try:
                    start = get_local_time(event.instance.vevent.dtstart.value)
                    days_with_events.add(start.date())
                    event_title = event.instance.vevent.summary.value if hasattr(event.instance.vevent, 'summary') else 'Unnamed event'
                    self.log_info(f"Event found: {start.strftime('%d.%m.')} - {event_title}")
                except Exception as e:
                    self.log_error(f"Error processing event: {e}")
            
            # Calculate free days
            free_days = all_days - days_with_events
            
            # Format the output
            message = FREE_DAYS_HEADER.format(
                start_date=start_date.strftime('%d.%m.'),
                end_date=end_date.strftime('%d.%m.')
            )
            
            if not free_days:
                message += "Keine freien Tage in den nächsten zwei Wochen."
            else:
                for date in sorted(free_days):
                    weekday = WEEKDAY_TRANSLATIONS[date.strftime("%A")]
                    message += f"{weekday}, {date.strftime('%d.%m.')}\n"
            
            message += FOOTER_TEXT
            
            return message

        except Exception as e:
            self.log_error(f"Error retrieving events: {e}")
            return "Error retrieving event data."

    def generate_week_overview(self) -> str:
        """
        Generates a weekly overview of all events.
        
        Returns:
            str: Formatted message with all events for the current week
        """
        if not self._calendar_client:
            return "Error connecting to calendar."

        current_time = get_local_time()
        
        # Calculate next Monday
        days_until_monday = 7 - current_time.weekday()  # Days until next Monday
        monday = current_time + timedelta(days=days_until_monday)
        monday = monday.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Calculate next Sunday
        next_sunday = monday + timedelta(days=6, hours=23, minutes=59, seconds=59)

        try:
            # Get all events in the time period
            events = self._calendar_client.search(
                start=monday,
                end=next_sunday,
                expand=True  # Expands recurring events
            )
            
            # Format the events
            formatted_events = []
            for event in events:
                try:
                    date, text = format_event(event)
                    sort_key = get_event_sort_key(event)
                    formatted_events.append((sort_key, text))
                except Exception as e:
                    self.log_error(f"Error formatting event: {e}")

            # Sort events by date
            formatted_events.sort(key=lambda x: x[0])

            # Create the message
            week_from = monday.strftime("%d.%m.")
            week_to = next_sunday.strftime("%d.%m.")
            message = WEEKLY_OVERVIEW_HEADER.format(
                start_date=week_from,
                end_date=week_to
            )

            for _, text in formatted_events:
                message += f"\n{text}\n"

            message += FOOTER_TEXT

            return message

        except Exception as e:
            self.log_error(f"Error retrieving events: {e}")
            return "Fehler beim Abrufen der Veranstaltungsdaten." 