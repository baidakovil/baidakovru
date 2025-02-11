from datetime import datetime

import requests

from ..config import FetcherConfig
from ..models import FetchResult
from .base import BaseFetcher, require_config


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
    def fetch(self) -> FetchResult:
        """Fetch and parse latest GitHub user activity events."""
        self.log_start()

        url = self.config.get_url()
        response = requests.get(url, headers=self.config.headers)
        result = self.create_base_result()

        if response.status_code == 200:
            events = response.json()
            result.raw_response = events

            try:
                if events:
                    sorted_events = sorted(
                        events, key=lambda x: x['created_at'], reverse=True
                    )
                    for event in sorted_events:
                        if event['type'] in self.config.supported_events:
                            result = self._process_event(event)
                            break
            except Exception as e:
                result.mark_as_error(f"Error parsing GitHub response: {str(e)}")
                return result

        elif response.status_code == 404:
            result.mark_as_error(f'GitHub user {self.config.username} not found')
            return result
        else:
            result.mark_as_error(f'GitHub API error: {response.status_code}')
            return result

        self.log_finish()
        return result

    def _process_event(self, event: dict) -> FetchResult:
        """Helper method to process a single GitHub event."""
        result = self.create_base_result()
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
