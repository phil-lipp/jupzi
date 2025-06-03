import asyncio
from datetime import datetime, timedelta
from telegram import Bot, Update
from telegram.error import TelegramError, TimedOut
from telegram.ext import Application, PollAnswerHandler, ContextTypes
from utils.logging_config import setup_logging, TESTING_ENVIRONMENT, TELEGRAM_TOKEN, TELEGRAM_CHAT_ID
from utils.templates import (
    POLL_QUESTION,
    POLL_OPTIONS,
    REMINDER_MESSAGE,
    SUCCESS_MESSAGE,
    POLL_SETTINGS,
    TIME_SETTINGS,
)

# Configure logging
logger = setup_logging('telegram_poll.log')

# Use template settings
MAIN_INTERVAL = TIME_SETTINGS["testing_interval"] if TESTING_ENVIRONMENT else TIME_SETTINGS["production_interval"]
CALCULATED_INTERVAL = MAIN_INTERVAL / TIME_SETTINGS["polling_divisor"]
POLLING_INTERVAL = 0 if CALCULATED_INTERVAL <= TIME_SETTINGS["base_polling_interval"] else CALCULATED_INTERVAL - TIME_SETTINGS["base_polling_interval"]

# Store poll information
current_poll = None
current_poll_message = None
poll_votes = set()  # Set to store unique voters

def get_next_monday():
    """Calculate the date of the next Monday."""
    today = datetime.now()
    days_until_monday = (7 - today.weekday()) % 7
    if days_until_monday == 0:  # If today is Monday
        days_until_monday = 7
    next_monday = today + timedelta(days=days_until_monday)
    return next_monday.strftime("%d.%m.")

async def send_poll(bot: Bot):
    """Send the weekly poll to the specified chat."""
    try:
        next_monday = get_next_monday()
        question = POLL_QUESTION.format(date=next_monday)
        
        message = await bot.send_poll(
            chat_id=TELEGRAM_CHAT_ID,
            question=question,
            options=POLL_OPTIONS,
            is_anonymous=POLL_SETTINGS["is_anonymous"],
            allows_multiple_answers=POLL_SETTINGS["allows_multiple_answers"]
        )
        
        global current_poll, current_poll_message
        current_poll = message.poll.id
        current_poll_message = message.message_id
        poll_votes.clear()  # Reset votes for new poll
        
        logger.info(f"Poll sent successfully for {next_monday}!")
        return message
    except TelegramError as e:
        logger.error(f"Error sending poll: {e}")
        return None

async def handle_poll_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle when someone votes in the poll."""
    if update.poll_answer.poll_id == current_poll:
        user_id = update.poll_answer.user.id
        poll_votes.add(user_id)
        logger.info(f"New vote received from user {user_id}. Total votes: {len(poll_votes)}")

async def send_reminder(bot: Bot):
    """Send a reminder if less than required people have voted."""
    required_votes = 1 if TESTING_ENVIRONMENT else 6  # Adjust based on environment
    current_votes = len(poll_votes)
    
    try:
        if current_votes < required_votes:
            await bot.send_message(
                chat_id=TELEGRAM_CHAT_ID,
                text=REMINDER_MESSAGE.format(required_votes=required_votes),
                reply_to_message_id=current_poll_message
            )
            logger.info(f"Reminder sent! Current votes: {current_votes}")
        else:
            await bot.send_message(
                chat_id=TELEGRAM_CHAT_ID,
                text=SUCCESS_MESSAGE.format(total_votes=current_votes),
                reply_to_message_id=current_poll_message
            )
            logger.info(f"Success message sent! Total votes: {current_votes}")
    except TelegramError as e:
        logger.error(f"Error sending message: {e}")

async def close_poll(bot: Bot):
    """Close the current poll."""
    if current_poll_message:
        try:
            await bot.stop_poll(
                chat_id=TELEGRAM_CHAT_ID,
                message_id=current_poll_message
            )
            logger.info("Poll closed successfully.")
        except TelegramError as e:
            logger.error(f"Error closing poll: {e}")

async def shutdown(application: Application):
    """Gracefully shutdown the application."""
    try:
        # Stop polling for updates
        await application.updater.stop()
        # Stop the application
        await application.stop()
        # Shutdown the application
        await application.shutdown()
        logger.info("Application shutdown complete")
    except TimedOut:
        logger.warning("Timeout during shutdown, but application was stopped successfully")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")

async def main():
    """Main function to send the poll and monitor results."""
    # Initialize the bot with increased connection pool size
    application = (
        Application.builder()
        .token(TELEGRAM_TOKEN)
        .connect_timeout(30.0)
        .read_timeout(30.0)
        .write_timeout(30.0)
        .pool_timeout(30.0)
        .build()
    )
    
    # Add handlers
    application.add_handler(PollAnswerHandler(handle_poll_answer))
    
    try:
        # Start the bot
        await application.initialize()
        await application.start()
        
        # Start polling for updates with calculated interval
        await application.updater.start_polling(poll_interval=POLLING_INTERVAL)
        logger.info(f"Started polling with interval of {POLLING_INTERVAL} seconds (effective interval will be {POLLING_INTERVAL + TIME_SETTINGS['base_polling_interval']}s)")
        
        # Send the initial poll
        await send_poll(application.bot)
        
        # Wait for first interval
        logger.info(f"Waiting for {MAIN_INTERVAL} seconds before sending reminder...")
        await asyncio.sleep(MAIN_INTERVAL)
        
        # Send reminder if needed
        await send_reminder(application.bot)
        
        # Wait for second interval
        logger.info(f"Waiting for {MAIN_INTERVAL} seconds before closing poll...")
        await asyncio.sleep(MAIN_INTERVAL)
        
        # Close the poll
        await close_poll(application.bot)
        
    finally:
        # Ensure proper shutdown
        await shutdown(application)

if __name__ == "__main__":
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        raise ValueError("Please set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in .env file")
    asyncio.run(main()) 