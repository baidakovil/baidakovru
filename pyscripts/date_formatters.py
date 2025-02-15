from datetime import datetime, time

import pytz
from flask_babel import format_date, format_datetime
from flask_babel import gettext as _

from .config import DATETIME_FORMAT


def format_time_ago(timestamp_str: str) -> str:
    """
    Convert timestamp to human-readable format
    """

    def pluralize(number, one, few, many):
        if 11 <= number % 100 <= 14:
            return many
        elif number % 10 == 1:
            return one
        elif 2 <= number % 10 <= 4:
            return few
        else:
            return many

    try:
        date = datetime.strptime(timestamp_str, DATETIME_FORMAT['db'])
        date = date.astimezone(pytz.utc)

        # Get the current time in the same time zone
        now = datetime.now(pytz.utc)
        diff = now - date

        if diff.days == 0:
            hours = diff.seconds // 3600
            if diff.seconds < 3600:  # Less than 1 hour
                return _('Только что')
            elif hours < 9:  # Between 1 and 9 hours
                return _(
                    '%(hour)d %(hour_word)s назад',
                    hour=hours,
                    hour_word=pluralize(hours, 'час', 'часа', 'часов'),
                )
            else:  # Between 9 and 24 hours
                return _('Сегодня')
        elif diff.days == 1:
            return _('Вчера')
        elif diff.days < 7:
            # Show full date without time for last week
            return _(
                '%(day)d %(day_word)s назад',
                day=diff.days,
                day_word=pluralize(diff.days, 'день', 'дня', 'дней'),
            )
        elif diff.days < 30:
            weeks = diff.days // 7
            return _(
                '%(week)d %(week_word)s назад',
                week=weeks,
                week_word=pluralize(weeks, 'неделя', 'недели', 'недель'),
            )
        elif diff.days < 365:
            months = diff.days // 30
            return _(
                '%(month)d %(month_word)s назад',
                month=months,
                month_word=pluralize(months, 'месяц', 'месяца', 'месяцев'),
            )
        else:
            years = diff.days // 365
            return _(
                '%(year)d %(year_word)s назад',
                year=years,
                year_word=pluralize(years, 'год', 'года', 'лет'),
            )
    except Exception:
        return _('Ошибка вычисления разницы дат')


def format_full_date(timestamp_str: str, locale: str = 'ru') -> str:
    """
    Format the timestamp for tooltip display using flask-babel.
    Uses 24-hour format for time and localized month names.
    """
    if not timestamp_str:
        return _('Нет даты')

    try:
        date = datetime.strptime(timestamp_str, DATETIME_FORMAT['db'])
        # First, let's see what we get from format_date
        formatted_date = format_date(date, "d MMMM y")
        return formatted_date

    except (ValueError, TypeError) as e:
        print(f"Debug - Error: {str(e)}")
        return _('Ошибка форматирования даты')
