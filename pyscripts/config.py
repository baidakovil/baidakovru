import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from dotenv import find_dotenv, load_dotenv
from flask_babel import lazy_gettext as _

from .log_config import setup_logging

logger = setup_logging()

# Constants for standardized datetime handling
DATETIME_FORMAT = {
    'db': '%Y-%m-%d %H:%M:%S',
    'iso': '%Y-%m-%dT%H:%M:%S%z',
}

EVENT_TYPES = {
    # GitHub events
    'github_push': _('Отправлен код в репозиторий'),
    'github_pr': _('Запрос на отправку кода'),
    'github_issue': _('Открыт новый вопрос'),
    'github_create': _('Создан новый репозиторий'),
    'github_fork': _('Сделан форк репозитория'),
    # iNaturalist events
    'inat_observation': _('Новое наблюдение'),
    # Telegram events
    'telegram_post': _('Новый пост'),
    # Last.fm events
    'lastfm_scrobble': _('Новое прослушивание'),
    # LinkedIn events
    'linkedin_post': _('Обновление информации'),
    # FlightRadar events
    'fr24_flight': _('Новый рейс'),
}


@dataclass
class FetcherConfig:
    """Configuration container for service-specific settings and credentials."""

    username: Optional[str] = None
    api_key: Optional[str] = None
    url_template: Optional[str] = None
    platform_name: str = "Unnamed Service"
    headers: Dict[str, str] = field(default_factory=dict)
    supported_events: List[str] = field(default_factory=list)
    date_format: Dict[str, str] = field(default_factory=dict)
    platform_url: Optional[str] = None

    def __post_init__(self):
        # Ensure date_format always includes the standardized output format
        if 'output' not in self.date_format:
            self.date_format['output'] = DATETIME_FORMAT['db']
        elif self.date_format['output'] != DATETIME_FORMAT['db']:
            logger.warning(
                f"Overriding non-standard output date format for {self.platform_name}"
            )
            self.date_format['output'] = DATETIME_FORMAT['db']

    def get_url(self) -> Optional[str]:
        """Format service URL template with available configuration values."""
        if not self.url_template:
            return None

        # Build template values from all non-None fields
        template_values = {}
        for field_name, field_value in vars(self).items():
            if field_value is not None:
                template_values[field_name] = field_value

        try:
            return self.url_template.format(**template_values)
        except KeyError:
            return None


class Config:
    """Central configuration manager that loads and provides access to all application settings."""

    def __init__(self):
        load_dotenv()

        # Database config
        self.db_path = os.getenv('DB_PATH')

        # GitHub specific configuration
        self.github = FetcherConfig(
            username=os.getenv('GITHUB_USERNAME'),
            platform_name="GitHub",
            url_template='https://api.github.com/users/{username}/events/public',
            platform_url=os.getenv('GITHUB_PLATFORM_URL'),
            headers={
                'Accept': 'application/vnd.github.v3+json',
            },
            supported_events=[
                'PushEvent',
                'PullRequestEvent',
                'IssuesEvent',
                'CreateEvent',
                'ForkEvent',
            ],
            date_format={'input': '%Y-%m-%dT%H:%M:%SZ'},
        )

        # iNaturalist specific configuration
        self.inat = FetcherConfig(
            username=os.getenv('INAT_USERNAME'),
            platform_name="iNaturalist",
            url_template='https://api.inaturalist.org/v1/observations?user_login={username}&order=desc&order_by=created_at',
            platform_url=os.getenv('INAT_PLATFORM_URL'),
            headers={
                'Accept': 'application/json',
            },
            date_format={'input': '%Y-%m-%dT%H:%M:%S%z'},
        )

        # Telegram specific configuration
        self.telegram = FetcherConfig(
            username=os.getenv('TELEGRAM_USERNAME'),
            platform_name="Telegram",
            url_template='https://t.me/s/{username}',
            platform_url=os.getenv('TELEGRAM_PLATFORM_URL'),
            headers={
                'Accept': 'text/html',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            },
            date_format={'input': '%Y-%m-%dT%H:%M:%S%z'},
        )

        # Last.fm specific configuration
        self.lastfm = FetcherConfig(
            username=os.getenv('LASTFM_USERNAME'),
            api_key=os.getenv('LASTFM_API_KEY'),
            platform_name="Last.fm",
            url_template='http://ws.audioscrobbler.com/2.0/?method=user.getrecenttracks&user={username}&api_key={api_key}&format=json&limit=1',
            platform_url=os.getenv('LASTFM_PLATFORM_URL'),
            headers={
                'Accept': 'application/json',
            },
            date_format={'input': '%d %b %Y, %H:%M'},
        )

        # LinkedIn specific configuration
        self.linkedin = FetcherConfig(
            username=os.getenv('LINKEDIN_USERNAME'),
            platform_name="LinkedIn",
            url_template='https://www.linkedin.com/in/{username}',
            platform_url=os.getenv('LINKEDIN_PLATFORM_URL'),
            date_format={'input': '%Y-%d-%m'},
        )

        # FlightRadar24 specific configuration
        self.flightradar = FetcherConfig(
            username=os.getenv('FLIGHTRADAR_USERNAME'),
            platform_name="myFlightradar24",
            url_template='https://my.flightradar24.com/{username}/flights',
            platform_url=os.getenv('FLIGHTRADAR_PLATFORM_URL'),
            headers={
                'Accept': 'text/html',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            },
            date_format={'input': '%Y-%m-%d'},
        )


# Global config instance
config = Config()
