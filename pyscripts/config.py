import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from dotenv import load_dotenv


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

    def get_url(self) -> Optional[str]:
        """Format service URL template with configured username."""
        if self.url_template and self.username:
            return self.url_template.format(username=self.username)
        return None


class Config:
    """Central configuration manager that loads and provides access to all application settings."""

    def __init__(self):
        load_dotenv()

        # Database config
        self.db_path = os.getenv('DB_PATH', 'database.db')

        # GitHub specific configuration
        self.github = FetcherConfig(
            username=os.getenv('GITHUB_USERNAME'),
            platform_name="GitHub",
            url_template='https://api.github.com/users/{username}/events/public',
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
            date_format={'input': '%Y-%m-%dT%H:%M:%SZ', 'output': '%Y-%m-%d %H:%M:%S'},
        )

        # iNaturalist specific configuration
        self.inat = FetcherConfig(
            username=os.getenv('INAT_USERNAME'),
            platform_name="iNaturalist",
            url_template='https://api.inaturalist.org/v1/observations?user_login={username}&order=desc&order_by=created_at',
            headers={
                'Accept': 'application/json',
            },
            date_format={'input': '%Y-%m-%dT%H:%M:%S%z', 'output': '%Y-%m-%d %H:%M:%S'},
        )

        # Telegram specific configuration
        self.telegram = FetcherConfig(
            username=os.getenv('TELEGRAM_USERNAME'),
            platform_name="Telegram",
            url_template='https://t.me/s/{username}',
            headers={
                'Accept': 'text/html',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            },
            date_format={'input': '%Y-%m-%dT%H:%M:%S%z', 'output': '%Y-%m-%d %H:%M:%S'},
        )

    @property
    def is_github_configured(self) -> bool:
        return bool(self.github.username)

    @property
    def is_inat_configured(self) -> bool:
        return bool(self.inat.username)

    @property
    def is_telegram_configured(self) -> bool:
        return bool(self.telegram.username)


# Global config instance
config = Config()
