"""
Template configuration for poll messages and settings.
Copy this file to templates.py and customize the values.
"""



# Poll question template
# Available placeholders:
# {date} - The date of the next Monday
POLL_QUESTION = "Who is attending the meeting on {date}?"

# Poll options
POLL_OPTIONS = [
    "I'm attending!",
    "I'm not attending :(", 
    "I'm still unsure"
]

# Reminder message template
# Available placeholders:
# {required_votes} - The minimum number of votes required
REMINDER_MESSAGE = "⚠️ Please participate in the poll! So far, less than {required_votes} people have voted."

# Success message template
# Available placeholders:
# {total_votes} - The total number of votes received
SUCCESS_MESSAGE = "Thank you for voting! 👍"

# Poll settings
POLL_SETTINGS = {
    "is_anonymous": False,  # Set to True if you want anonymous polls
    "allows_multiple_answers": False,  # Set to True if you want to allow multiple selections
}

# Time settings (in seconds)
TIME_SETTINGS = {
    "testing_interval": 60,  # 1 minute for testing
    "production_interval": 24 * 60 * 60,  # 24 hours for production
    "polling_divisor": 6,  # Divide the main interval by this to get polling interval
    "base_polling_interval": 10,  # Base interval that gets added to our setting
}

# Common footer text used in multiple scripts
FOOTER_TEXT = (
    "\n\nWe are always happy to hear your feedback!"
)

# Common weekday translations
WEEKDAY_TRANSLATIONS = {
    "Monday": "Montag",
    "Tuesday": "Dienstag",
    "Wednesday": "Mittwoch",
    "Thursday": "Donnerstag",
    "Friday": "Freitag",
    "Saturday": "Samstag",
    "Sunday": "Sonntag"
}

# Common message headers
FREE_DAYS_HEADER = "Here are the free days in the next two weeks ({start_date} - {end_date}):\n"
WEEKLY_OVERVIEW_HEADER = "Here's the weekly overview ({start_date}. - {end_date}.):\n" 