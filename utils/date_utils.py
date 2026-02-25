import dateparser
from datetime import datetime

def normalize_date(natural_date: str) -> str:
    """
    Converts natural language date into YYYY-MM-DD format.
    Example:
        "Tomorrow" -> "2026-02-26"
        "26 February" -> "2026-02-26"
    """

    parsed_date = dateparser.parse(
        natural_date,
        settings={
            "PREFER_DATES_FROM": "future"
        }
    )

    if not parsed_date:
        raise ValueError("Could not understand the date.")

    return parsed_date.strftime("%Y-%m-%d")




def normalize_time(natural_time: str) -> str:
    """
    Converts natural language time into HH:MM 24-hour format.
    Example:
        "10 AM" -> "10:00"
        "4 pm" -> "16:00"
    """

    parsed_time = dateparser.parse(natural_time)

    if not parsed_time:
        raise ValueError("Could not understand the time.")

    return parsed_time.strftime("%H:%M")