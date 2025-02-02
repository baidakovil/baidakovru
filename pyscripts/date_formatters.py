from datetime import datetime

from flask_babel import format_date, format_datetime
from flask_babel import gettext as _

from .config import DATETIME_FORMAT


def format_time_ago(timestamp_str: str) -> str:
    """
    Convert timestamp to human-readable format
    """
    try:
        date = datetime.strptime(timestamp_str, DATETIME_FORMAT['db'])
        now = datetime.now()
        diff = now - date

        if diff.days == 0:
            hours = diff.seconds // 3600
            if diff.seconds < 3600:  # Less than 1 hour
                return _('Прям вот-вот')
            elif hours < 9:  # Between 1 and 9 hours
                return _('%(hour)d часов назад', hour=hours)
            else:  # Between 9 and 24 hours
                return _('Сегодня')
        elif diff.days < 7:
            # Show full date without time for last week
            return _('%(day)d дней назад', day=diff.days)
        elif diff.days < 30:
            weeks = diff.days // 7
            return _('%(week)d недель назад', week=weeks)
        elif diff.days < 365:
            months = diff.days // 30
            return _('%(month)d месяцев назад', month=months)
        else:
            years = diff.days // 365
            return _('%(year)d лет назад', year=years)
    except Exception:
        return _('Неверная дата')


def format_full_date(timestamp_str: str, locale: str = 'ru') -> str:
    """
    Format the timestamp for tooltip display using flask-babel.
    Shows time only if it's not 00:00:00.
    Uses 24-hour format for time and localized month names.
    """
    try:
        date = datetime.strptime(timestamp_str, DATETIME_FORMAT['db'])
        if date.hour == 0 and date.minute == 0 and date.second == 0:
            # Show only date
            formatted = format_date(date, format='full')
        else:
            # Show full date and time in 24-hour format with localized preposition
            formatted = (
                format_datetime(date, "EEEE, d MMMM y")
                + _(' в ')
                + format_datetime(date, "HH:mm")
            )
        return formatted
    except Exception as e:
        return _('Неверная дата')
