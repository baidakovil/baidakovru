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
    public_name: str = "Unnamed Service"
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
            public_name="GitHub",
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

    @property
    def is_github_configured(self) -> bool:
        return bool(self.github.username)


# Global config instance
config = Config()
