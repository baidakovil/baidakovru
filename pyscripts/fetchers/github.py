from datetime import datetime

import requests

from ..config import FetcherConfig
from ..models import FetchResult
from .base import BaseFetcher


class GitHubFetcher(BaseFetcher):
    @property
    def platform_id(self) -> str:
        return 'github'

    def validate_config(self) -> bool:
        if not self.config.username:
            self.logger.error("GitHub username not configured")
            return False
        if not self.config.get_url():
            self.logger.error("GitHub URL configuration is invalid")
            return False
        return True

    def fetch(self) -> FetchResult:
        """Fetch and parse latest GitHub user activity events."""
        self.log_start()

        if not self.validate_config():
            self.logger.error(
                f'Config for {self.platform_id} was not validated. Returning empty result.'
            )
            return FetchResult.create_empty(self.platform_id, self.config.public_name)

        url = self.config.get_url()
        response = requests.get(url, headers=self.config.headers)
        result = FetchResult.create_empty(self.platform_id, self.config.public_name)

        if response.status_code == 200:
            events = response.json()
            result.raw_response = events
            self.logger.debug(
                f'Fetched {len(events)} events from GitHub for {self.config.username}'
            )

            if events:
                sorted_events = sorted(
                    events, key=lambda x: x['created_at'], reverse=True
                )
                for event in sorted_events:
                    if event['type'] in self.config.supported_events:
                        result.raw_datetime = event['created_at']
                        result.formatted_datetime = (
                            datetime.strptime(
                                event['created_at'], self.config.date_format['input']
                            )
                            .strftime(self.config.date_format['output'])
                            .lower()
                        )
                        result.update_desc = f"{event['type']} at repo {event['repo']['name']} at {event['repo']['url']}"
                        break

        elif response.status_code == 404:
            self.logger.error(
                f'404 when fetching updates from GitHub for {self.config.username}'
            )
        else:
            self.logger.error(
                f'Error when fetching updates from GitHub for {self.config.username}: {response.status_code}'
            )

        self.log_finish()
        return result
