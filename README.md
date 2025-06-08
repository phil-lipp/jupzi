# Jupibar

A calendar and meeting management system.

## Project Structure

```
jupzi/
├── app/
│   ├── core/
│   │   ├── bot/
│   │   │   ├── bot.py           # Main bot class
│   │   │   ├── handlers.py      # Message handlers
│   │   │   └── commands.py      # Command implementations
│   │   ├── scheduler/
│   │   │   ├── scheduler.py     # Job scheduler
│   │   │   └── jobs.py         # Job implementations
│   │   └── persistence/
│   │       ├── state.py        # State management
│   │       └── storage.py      # Storage interface
│   ├── models/                  # Database models (already OOP)
│   ├── services/
│   │   ├── calendar.py         # Calendar service
│   │   ├── telegram.py         # Telegram service
│   │   └── poll.py            # Poll service
│   └── utils/
│       ├── config.py           # Configuration management
│       └── logging.py          # Logging utilities
├── logs/                  # Application logs
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker configuration
└── docker-compose.yml    # Docker Compose configuration
```

# Various Telegram Scripts
This repository contains a collection of Telegram bots and scripts for managing group meetings and schedules:

- **Telegram Poll Bot**: Sends automated weekly polls to track meeting attendance, with configurable reminders and settings.
- **Weekly Overview Bot**: Provides a weekly summary of upcoming events and activities.
- **Free Dates Bot**: Checks a CalDAV calendar and reports available dates in the next 2 weeks, with localized weekday names.

The scripts use:
- python-telegram-bot for Telegram integration
- caldav for calendar access
- Structured logging with rotating log files
- Environment variables for configuration
- Customizable message templates
- Support for testing and production environments
- PostgreSQL database for state management and job orchestration
- Docker for containerization

Key features across the scripts:
- Robust error handling and logging
- Timezone awareness
- Configurable timing intervals
- Localization support
- Clean separation of configuration and logic
- State persistence and recovery
- Job orchestration and scheduling

## Setup

### Option 1: Docker Setup (Recommended)

1. Clone this repository
2. Copy `.env-example` to `.env` and fill in your values:
   ```bash
   cp .env-example .env
   ```
3. Set up your environment variables in `.env`:
   - `TELEGRAM_BOT_TOKEN`: Your Telegram bot token from [@BotFather](https://t.me/botfather)
   - `TELEGRAM_CHAT_ID`: The chat ID where the bot will send polls
   - Database configuration (already set in .env-example)
4. Start the application:
   ```bash
   docker-compose up --build
   ```

### Option 2: Local Setup

1. Clone this repository
   ```bash
   git clone https://github.com/phil-lipp/jupzi.git
   ```

   to update use:
   ```bash
   cd jupzi
   git pull
   ```
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
# With Docker
docker-compose up

# Without Docker
python meeting_poll.py
```

The bot will:
1. Send a weekly poll asking about attendance for the next Monday
2. Send a reminder if not enough people have voted
3. Close the poll after 48 hours
4. Store poll state in the database for recovery if interrupted

### Run the weekly overview query:
```bash
# With Docker
docker-compose up

# Without Docker
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
6. Store the query results in the database

### Run the free dates query: 
```bash
# With Docker
docker-compose up

# Without Docker
python free_dates.py
```

The script will:
1. Check the provided calendar
2. Look at the next 14 days
3. Filter out any days that have an event, which __starts__ on that day.
4. List all remaining days.
5. Send the messsage via the Telegram Bot to the Telegram Channel/Chat
6. Store the query results in the database

## Dependencies

- python-telegram-bot==20.7
- python-dotenv==1.0.0
- caldav>=1.0.0
- requests>=2.31.0
- pytz>=2024.1
- sqlalchemy>=2.0
- psycopg2-binary>=2.9
- alembic>=1.11
- pytest>=7.0

## Database

The application uses PostgreSQL for:
- Storing poll states and responses
- Job orchestration and scheduling
- Event history and metadata
- State recovery after interruptions

Database migrations are managed using Alembic. To run migrations:
```bash
# With Docker
docker-compose exec app alembic upgrade head

# Without Docker
alembic upgrade head
```
