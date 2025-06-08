import asyncio
import logging
import sys
import json
from pathlib import Path
from datetime import datetime

from app.core.config import Config
from app.core.bot.bot import JupziBot

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        if hasattr(record, 'correlation_id'):
            log_record['correlation_id'] = record.correlation_id
            
        if record.exc_info:
            log_record['exception'] = self.formatException(record.exc_info)
            
        return json.dumps(log_record)

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Console handler with JSON formatting
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(JsonFormatter())
logger.addHandler(console_handler)

# File handler for persistent logs
log_file = Path("logs/jupzi.log")
log_file.parent.mkdir(exist_ok=True)
file_handler = logging.FileHandler(log_file)
file_handler.setFormatter(JsonFormatter())
logger.addHandler(file_handler)

async def main():
    """Main application entry point."""
    try:
        # Load configuration
        config = Config.from_env()
        
        # Initialize bot
        bot = JupziBot(config)
        
        # Start bot
        bot.start()
        
        # Keep the application running
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        raise
    finally:
        if 'bot' in locals():
            bot.stop()

if __name__ == "__main__":
    asyncio.run(main()) 