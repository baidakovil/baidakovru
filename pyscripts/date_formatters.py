from datetime import datetime

from flask_babel import format_date, format_datetime
from flask_babel import gettext as _

from .config import DATETIME_FORMAT


def format_time_ago(timestamp_str: str) -> str:
    """
    Convert timestamp to human-readable format with the following rules:
    - "Just now" if less than 1 hour ago
    - "X hours ago" if between 1 and 9 hours ago
    - "Today" if between 9 and 24 hours ago
    - Full date (without time) if less than 7 days ago
    - Weeks/months/years ago for older dates
    """
    try:
        date = datetime.strptime(timestamp_str, DATETIME_FORMAT['db'])
        now = datetime.now()
        diff = now - date

        if diff.days == 0:
            hours = diff.seconds // 3600
            if diff.seconds < 3600:  # Less than 1 hour
                return _('Just now')
            elif hours < 9:  # Between 1 and 9 hours
                return _('%(hour)d hours ago', hour=hours)
            else:  # Between 9 and 24 hours
                return _('Today')
        elif diff.days < 7:
            # Show full date without time for last week
            return _('%(day)d days ago', day=diff.days)
        elif diff.days < 30:
            weeks = diff.days // 7
            return _('%(week)d weeks ago', week=weeks)
        elif diff.days < 365:
            months = diff.days // 30
            return _('%(month)d months ago', month=months)
        else:
            years = diff.days // 365
            return _('%(year)d years ago', year=years)
    except Exception:
        return _('Invalid date')


def format_full_date(timestamp_str: str, locale: str = 'ru') -> str:
    """
    Format the timestamp for tooltip display using flask-babel.
    Shows time only if it's not 00:00:00.
    """
    try:
        date = datetime.strptime(timestamp_str, DATETIME_FORMAT['db'])
        if date.hour == 0 and date.minute == 0 and date.second == 0:
            # Show only date
            formatted = format_date(date, format='long')
        else:
            # Show full date and time
            formatted = format_datetime(date, format='long')
        return formatted
    except Exception as e:
        return _('Invalid date')
