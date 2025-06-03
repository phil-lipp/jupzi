import logging
import os
import inspect
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Common logging format
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# Ensure logs directory exists
LOGS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
os.makedirs(LOGS_DIR, exist_ok=True)

def setup_logging(log_file: str) -> logging.Logger:
    """
    Set up logging with a consistent format for all scripts.
    
    Args:
        log_file (str): Name of the log file
        
    Returns:
        logging.Logger: Configured logger instance
    """
    # Get the caller's script name
    frame = inspect.stack()[1]
    script_path = frame.filename
    script_name = os.path.basename(script_path)
    
    logger = logging.getLogger(script_name)
    logger.setLevel(logging.INFO)
    
    # Create formatters
    formatter = logging.Formatter(LOG_FORMAT)
    
    # Create handlers
    log_path = os.path.join(LOGS_DIR, log_file)
    file_handler = logging.FileHandler(log_path)
    file_handler.setFormatter(formatter)
    
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    
    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(stream_handler)
    
    return logger


# Testing environment
TESTING_ENVIRONMENT = os.getenv('TESTING_ENVIRONMENT', True) # Default to True if not specified

# Telegram configuration
TELEGRAM_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

# Calendar configuration
CALDAV_URL = os.getenv('CALDAV_URL')
CALENDAR_PATH = os.getenv('CALENDAR_PATH')
CALDAV_USERNAME = os.getenv('CALDAV_USERNAME')
CALDAV_PASSWORD = os.getenv('CALDAV_PASSWORD')

# Timezone configuration
TIMEZONE = os.getenv('TIMEZONE', 'Europe/Berlin')  # Default to Berlin if not specified 