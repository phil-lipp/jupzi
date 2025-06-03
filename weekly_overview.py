import requests
from datetime import timedelta
from utils.logging_config import setup_logging, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID
from utils.templates import FOOTER_TEXT, WEEKLY_OVERVIEW_HEADER
from utils.calendar_utils import get_calendar_client, get_local_time, format_event, get_event_sort_key

# Configure logging
logger = setup_logging('wochenuebersicht.log')

def generate_week_overview() -> str:
    """
    Generates a weekly overview of all events.
    
    Returns:
        str: Formatted message with all events for the current week
    """
    calendar = get_calendar_client()
    if not calendar:
        return "Error connecting to calendar."

    current_time = get_local_time()
    
    # Calculate next Monday
    days_until_monday = 7 - current_time.weekday()  # Days until next Monday
    monday = current_time + timedelta(days=days_until_monday)
    monday = monday.replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Calculate next Sunday
    next_sunday = monday + timedelta(days=6, hours=23, minutes=59, seconds=59)

    logger.info(f"Current date: {current_time.strftime('%d.%m. %H:%M:%S')}")
    logger.info(f"Time period: {monday.strftime('%d.%m. %H:%M:%S')} - {next_sunday.strftime('%d.%m. %H:%M:%S')}")

    try:
        # Get all events in the time period with the new search method
        events = calendar.search(
            start=monday,
            end=next_sunday,
            expand=True  # Expands recurring events
        )
        
        logger.info(f"Found events: {len(events)}")
        
        # Format the events
        formatted_events = []
        for event in events:
            try:
                date, text = format_event(event)
                sort_key = get_event_sort_key(event)
                formatted_events.append((sort_key, text))
                logger.info(f"Event formatted: {date} - {event.instance.vevent.summary.value if hasattr(event.instance.vevent, 'summary') else 'Unnamed event'}")
            except Exception as e:
                logger.error(f"Error formatting event: {e}")
                # Try to get basic event info for logging
                try:
                    event_info = f"Event: {event.instance.vevent.summary.value if hasattr(event.instance.vevent, 'summary') else 'Unnamed event'}"
                    logger.error(f"Error with event: {event_info}")
                except:
                    logger.error("Error formatting an event (no additional details available)")

        # Sort events by date
        formatted_events.sort(key=lambda x: x[0])

        # Create the message
        week_from = monday.strftime("%d.%m")
        week_to = next_sunday.strftime("%d.%m")
        message = WEEKLY_OVERVIEW_HEADER.format(
            start_date=week_from,
            end_date=week_to
        )

        for _, text in formatted_events:
            message += f"\n{text}\n"

        message += FOOTER_TEXT

        return message

    except Exception as e:
        logger.error(f"Error retrieving events: {e}")
        return "Fehler beim Abrufen der Veranstaltungsdaten."

def send_to_telegram(message: str, token: str, chat_id: str) -> None:
    """
    Sends the weekly overview to a Telegram channel.
    
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
    logger.info("Starting weekly overview generation")
    message = generate_week_overview()
    logger.info("Weekly overview generated")
    
    send_to_telegram(message, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID)
    logger.info("Weekly overview processing completed")
