import requests
from datetime import timedelta
from utils.logging_config import setup_logging, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID
from utils.templates import WEEKDAY_TRANSLATIONS, FOOTER_TEXT, FREE_DAYS_HEADER
from utils.calendar_utils import get_calendar_client, get_local_time

# Configure logging
logger = setup_logging('freie_tage.log')

def get_free_days() -> str:
    """
    Generates a list of days without events in the next two weeks.
    
    Returns:
        str: Formatted message with all free days
    """
    calendar = get_calendar_client()
    if not calendar:
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
        # Get all events in the period with the new search method
        events = calendar.search(
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
                logger.info(f"Event found: {start.strftime('%d.%m.')} - {event_title}")
            except Exception as e:
                logger.error(f"Error processing event: {e}")
                # Try to get basic event info for logging
                try:
                    event_info = f"Event: {event.instance.vevent.summary.value if hasattr(event.instance.vevent, 'summary') else 'Unnamed event'}"
                    logger.error(f"Error with event: {event_info}")
                except:
                    logger.error("Error processing an event (no additional details available)")
        
        # Calculate free days
        free_days = all_days - days_with_events
        
        logger.info(f"Found days with events: {sorted(days_with_events)}")
        logger.info(f"Found free days: {sorted(free_days)}")
        
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
        logger.error(f"Error retrieving events: {e}")
        return "Error retrieving event data."

def send_to_telegram(message: str, token: str, chat_id: str) -> None:
    """
    Sends the message to a Telegram channel.
    
    Args:
        message (str): The message to send
        token (str): The Telegram Bot Token
        chat_id (str): The target channel's Chat ID
    """
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        response = requests.post(url, data=data)
        response.raise_for_status()
        logger.info("Message successfully sent via Telegram")
    except requests.RequestException as e:
        logger.error(f"Error sending via Telegram: {e}")

if __name__ == "__main__":
    logger.info("Starting free days generation")
    message = get_free_days()
    logger.info("Free days generated")
    
    send_to_telegram(message, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID)
    logger.info("Free days processing completed") 