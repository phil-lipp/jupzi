"""
Common calendar utilities used across scripts.
"""
import caldav
import pytz
from datetime import datetime, timedelta
from typing import Optional, List, Tuple, Union
from caldav.lib.error import AuthorizationError
from utils.logging_config import setup_logging, CALDAV_URL, CALENDAR_PATH, TIMEZONE, CALDAV_USERNAME, CALDAV_PASSWORD
from utils.templates import WEEKDAY_TRANSLATIONS

# Configure logging
logger = setup_logging('calendar_utils.log')

def get_calendar_client() -> Optional[caldav.Calendar]:
    """
    Creates and returns a CalDAV calendar client.
    
    Returns:
        Optional[caldav.Calendar]: The calendar client or None if connection fails
    """
    try:
        client = caldav.DAVClient(
            url=CALDAV_URL,
            username=CALDAV_USERNAME,
            password=CALDAV_PASSWORD
        )
        calendar = client.calendar(url=f"{CALDAV_URL}{CALENDAR_PATH}")
        return calendar
    except AuthorizationError as e:
        logger.error(f"Authorization failed when connecting to calendar: {e}")
        return None
    except Exception as e:
        logger.error(f"Error connecting to calendar: {e}")
        return None

def get_local_time(dt: Optional[datetime] = None) -> datetime:
    """
    Get time in the configured local timezone.
    
    Args:
        dt (Optional[datetime]): Datetime to convert to local timezone. If None, returns current time.
        
    Returns:
        datetime: Time in local timezone
    """
    local_tz = pytz.timezone(TIMEZONE)
    if dt is None:
        return datetime.now(local_tz)
    if dt.tzinfo is None:
        dt = local_tz.localize(dt)
    return dt.astimezone(local_tz)

def get_event_sort_key(event) -> Union[datetime.date, datetime]:
    """
    Get a sort key for an event, handling both datetime and date objects.
    
    Args:
        event: A caldav.Event object
        
    Returns:
        Union[datetime.date, datetime]: A sortable key for the event
    """
    start = event.instance.vevent.dtstart.value
    if isinstance(start, datetime):
        start = get_local_time(start)
        return start.date()
    return start

def format_event(event) -> Tuple[str, str]:
    """
    Format a calendar event into a readable format.
    
    Args:
        event: A caldav.Event object
        
    Returns:
        tuple: (date, text) - Formatted date and event text
    """
    try:
        # Handle start time
        start = event.instance.vevent.dtstart.value
        
        # Check if it's a datetime or date object
        if isinstance(start, datetime):
            start = get_local_time(start)
            weekday_en = start.strftime("%A")
            date = f"{weekday_en} {start.strftime('%d.%m')}."
            time_range = f"{start.strftime('%H:%M')}"
        else:  # date object (all-day event)
            weekday_en = start.strftime("%A")
            date = f"{weekday_en} {start.strftime('%d.%m')}."
            time_range = "Ganztägig"

        # Handle end time
        end = event.instance.vevent.dtend.value
        
        if isinstance(end, datetime):
            end = get_local_time(end)
            if isinstance(start, datetime):
                if start.date() == end.date():
                    time_range += f" - {end.strftime('%H:%M')}"
                else:
                    time_range += " - OpenEnd"
            else:
                time_range += " - OpenEnd"
        else:  # date object (all-day event)
            if start != end:  # If end date is different from start date
                # Subtract one day from end date since CalDAV stores end date as day after event
                last_day = end - timedelta(days=1)
                time_range += f" bis einschließlich {last_day.strftime('%d.%m')}."

        weekday = WEEKDAY_TRANSLATIONS[weekday_en]

        # Safely get event properties
        try:
            original_title = event.instance.vevent.summary.value if hasattr(event.instance.vevent, 'summary') else "Unbenannter Termin"
        except Exception:
            original_title = "Unbenannter Termin"

        try:
            description = event.instance.vevent.description.value if hasattr(event.instance.vevent, 'description') else "Keine Beschreibung vorhanden."
        except Exception:
            description = "Keine Beschreibung vorhanden."

        # Detect + prune "rauchfrei" and surrounding brackets
        if "rauchfrei" in original_title.lower():
            smoking_info = "Rauchfrei"
            # Remove "rauchfrei" and any surrounding brackets
            title = original_title
            title = title.replace("(rauchfrei)", "").replace("[rauchfrei]", "").replace("{rauchfrei}", "")
            title = title.replace("(Rauchfrei)", "").replace("[Rauchfrei]", "").replace("{Rauchfrei}", "")
            title = title.replace("rauchfrei", "").replace("Rauchfrei", "")
            title = title.strip(":,- ()[]{}")  # Remove any remaining brackets and separators
        else:
            smoking_info = "Rauchkneipe"
            title = original_title

        title = title.split(",", 1)[0]

        text = (
            f"  🗓  {date}\n"
            f"  🕖  {time_range}\n"
            f"  🃏  {title}\n"
            f"  🫧  {description}\n"
            f"  🪩  {smoking_info}"
        )

        # Replace English weekday with German
        for en, de in WEEKDAY_TRANSLATIONS.items():
            text = text.replace(en, de)

        logger.debug(f"Event formatted: {date} - {title}")
        return date, text
        
    except Exception as e:
        logger.error(f"Error formatting event: {e}")
        # Try to get basic event info for logging
        try:
            event_info = f"Event: {event.instance.vevent.summary.value if hasattr(event.instance.vevent, 'summary') else 'Unnamed event'}"
            logger.error(f"Error with event: {event_info}")
        except:
            logger.error("Error formatting an event (no additional details available)")
        raise  # Re-raise the exception to be handled by the caller 