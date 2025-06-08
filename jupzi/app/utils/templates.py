"""
Template configuration for poll messages and settings.
Copy this file to templates.py and customize the values.
"""



# Poll question template
# Available placeholders:
# {date} - The date of the next Monday
POLL_QUESTION = "Wer kommt zum Plenum am {date}?"

# Poll options
POLL_OPTIONS = [
    "Ich bin dabei!",
    "Ich bin raus :(", 
    "Ich bin noch unsicher"
]

# Reminder message template
# Available placeholders:
# {required_votes} - The minimum number of votes required
REMINDER_MESSAGE = "⚠️ Bitte an der Umfrage teilnehmen! Bisher haben weniger als {required_votes} Personen abgestimmt."

# Success message template
SUCCESS_MESSAGE = "Danke für's abstimmen! 👍"

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
    "\n\nHast du Lust auch mal in der Jupibar zu veranstalten? Dann schicke eine Anfrage mit den Rahmenangaben (Datum, Uhrzeit, Art der Veranstaltung, Besonderheiten) an va-jupi@das-gaengeviertel.info"
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
FREE_DAYS_HEADER = "Hier sind die freien Tage in den nächsten zwei Wochen ({start_date} - {end_date}):\n"
WEEKLY_OVERVIEW_HEADER = "Hier sind die geplanten Veranstaltungen für nächste Woche ({start_date} - {end_date}):\n"