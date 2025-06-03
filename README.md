# Various Telegram Scripts
This repository contains a collection of Telegram bots and scripts for managing group meetings and schedules:

- **Telegram Poll Bot**: Sends automated weekly polls to track meeting attendance, with configurable reminders and settings
- **Weekly Overview Bot**: Provides a weekly summary of upcoming events and activities (implementation details not shown in codebase)
- **Free Dates Bot**: Checks a CalDAV calendar and reports available dates in the next 2 weeks, with localized weekday names

The scripts use:
- python-telegram-bot for Telegram integration
- caldav for calendar access
- Structured logging with rotating log files
- Environment variables for configuration
- Customizable message templates
- Support for testing and production environments

Key features across the scripts:
- Robust error handling and logging
- Timezone awareness
- Configurable timing intervals
- Localization support
- Clean separation of configuration and logic

## Setup

1. Clone this repository
2. Create a virtual environment and activate it:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Copy `.env-example` to `.env` and fill in your values:
   ```bash
   cp .env-example .env
   ```
5. Set up your environment variables in `.env`:
   - `TELEGRAM_BOT_TOKEN`: Your Telegram bot token from [@BotFather](https://t.me/botfather)
   - `TELEGRAM_CHAT_ID`: The chat ID where the bot will send polls. To get a list of Chat IDs, visit: `https://api.telegram.org/bot<TELEGRAM_BOT_TOKEN>/getUpdates`.

6. Copy `utils/templates-example.py` to `utils/templates.py`:
   ```bash
   cp utils/templates-example.py utils/templates.py
   ```

7. Set up the template variables in `utils/templates.py`:
   - `POLL_QUESTION`: Template for the poll question (use {date} placeholder)
   - `POLL_OPTIONS`: List of poll options
   - `REMINDER_MESSAGE`: Template for reminder message (use {required_votes} placeholder)
   - `SUCCESS_MESSAGE`: Template for success message 
   - `POLL_SETTINGS`: Configure poll behavior (anonymous, multiple answers)
   - `TIME_SETTINGS`: Configure timing intervals for testing and production
   - `FOOTER_TEXT`: Text footer which is send with the weekly overview and free days messages.
   - `WEEKDAY_TRANSLATIONS`: Provide a dictionary to translate english weekdays into your locale. E.g. "Monday": "Montag", "Tuesday": "Dienstag", ...
   - `FREE_DAYS_HEADER`: Text Header which is added to the free days message. You can include "{} - {}", which will be filled with the start and end date of the interval.
   - `WEEKLY_OVERVIEW_HEADER`: Same behaviour as `FREE_DAYS_HEADER`.

8. Set up cronjobs to run either of the scripts on a regular basis.

## Usage

### Run the bot:
```bash
python telegram_poll_bot.py
```

The bot will:
1. Send a weekly poll asking about attendance for the next Monday
2. Send a reminder if not enough people have voted
3. Close the poll after 48 hours


### Run the weekly overview query:
```bash
python weekly_overview.py
```

The script will:
1. Check the provided calendar
2. Calculate the next monday and the sunday after that (this will be the time range)
3. Get all events in the time range
4. Format the events, e.g.
```markdown
  🗓  Saturday 14.06.
  🕖  19:00 - OpenEnd
  🃏  Event X
  🫧  No Description.
  🪩  smokefree
```
5. Send the message via the Telegram Bot to the Telegram Channel/Chat


### Run the free dates query: 
```bash
python free_dates.py
```

The script will:
1. Check the provided calendar
2. Look at the next 14 days
3. Filter out any days that have an event, which __starts__ on that day.
4. List all remaining days.
5. Send the messsage via the Telegram Bot to the Telegram Channel/Chat


## Dependencies

- python-telegram-bot==20.7
- python-dotenv==1.0.0
- caldav>=1.0.0
- requests>=2.31.0
- pytz>=2024.1