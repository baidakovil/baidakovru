from datetime import datetime

import requests

from ..config import FetcherConfig
from ..models import FetchResult
from .base import BaseFetcher, error_handler, require_config


class GitHubFetcher(BaseFetcher):
    @property
    def platform_id(self) -> str:
        return 'github'

    def validate_config(self) -> bool:
        return bool(self.config.username and self.config.get_url())

    EVENT_TYPE_MAPPING = {
        'PushEvent': 'github_push',
        'PullRequestEvent': 'github_pr',
        'IssuesEvent': 'github_issue',
        'CreateEvent': 'github_create',
        'ForkEvent': 'github_fork',
    }

    @require_config
    @error_handler
    def fetch(self) -> FetchResult:
        """Fetch and parse latest GitHub user activity events."""
        url = self.config.get_url()
        response = requests.get(url, headers=self.config.headers)

        if response.status_code == 404:
            return self.create_error_result(
                f'GitHub user {self.config.username} not found'
            )
        if response.status_code != 200:
            return self.create_error_result(f'GitHub API error: {response.status_code}')

        events = response.json()
        result = self.create_base_result(events)

        if not events:
            return self.create_error_result('No events found in GitHub response')

        sorted_events = sorted(events, key=lambda x: x['created_at'], reverse=True)
        for event in sorted_events:
            if event['type'] in self.config.supported_events:
                return self._process_event(event)

        return self.create_error_result('No supported events found')

    def _process_event(self, event: dict) -> FetchResult:
        """Process a single GitHub event."""
        result = self.create_base_result(event)
        result.raw_datetime, result.formatted_datetime = self.format_date(
            event['created_at']
        )

        if event['type'] == 'PushEvent':
            commits = event['payload'].get('commits', [])
            if commits:
                result.update_url = commits[-1]['url'].replace(
                    'api.github.com/repos', 'github.com'
                )

        result.update_event = self.EVENT_TYPE_MAPPING.get(event['type'])
        result.update_desc = f"{event['type']} to repository"
        return result
