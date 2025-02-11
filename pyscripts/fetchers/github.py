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
        try:
            response = requests.get(url, headers=self.config.headers)
            result = self.create_base_result()  # Create base result for success case

            if response.status_code == 200:
                events = response.json()
                result.raw_response = events
                self.logger.debug(
                    f'Fetched {len(events)} events from GitHub for {self.config.username}'
                )

                try:
                    if events:
                        sorted_events = sorted(
                            events, key=lambda x: x['created_at'], reverse=True
                        )
                        for event in sorted_events:
                            if event['type'] in self.config.supported_events:
                                result.raw_datetime, result.formatted_datetime = (
                                    self.format_date(event['created_at'])
                                )

                                # Extract correct URL based on event type
                                if event['type'] == 'PushEvent':
                                    # Get URL of the last commit in the push
                                    commits = event['payload'].get('commits', [])
                                    if commits:
                                        result.update_url = commits[-1]['url'].replace(
                                            'api.github.com/repos', 'github.com'
                                        )
                                elif event['type'] == 'ReleaseEvent':
                                    result.update_url = event['payload']['release'][
                                        'html_url'
                                    ]
                                else:
                                    # Fallback to repo URL if event type is unknown
                                    result.update_url = event['repo']['url'].replace(
                                        'api.github.com/repos', 'github.com'
                                    )

                                result.update_event = self.EVENT_TYPE_MAPPING.get(
                                    event['type']
                                )
                                result.update_desc = f"{event['type']} to repository"
                                break
                except Exception as e:
                    self.logger.error(f'Error parsing GitHub response: {e}')
                    # Keep raw_response but mark parsing error in desc
                    result.update_desc = f"Error parsing update: {str(e)}"

            elif response.status_code == 404:
                self.logger.error(
                    f'404 when fetching updates from GitHub for {self.config.username}'
                )
                result.raw_response = {'error': 'Not Found', 'status': 404}
            else:
                self.logger.error(
                    f'Error when fetching updates from GitHub for {self.config.username}: {response.status_code}'
                )
                result.raw_response = {
                    'error': 'Bad Response',
                    'status': response.status_code,
                }

        except Exception as e:
            self.logger.error(f'Error fetching from GitHub: {e}')
            result = self.create_base_result(
                {'error': str(e)}
            )  # Create base result with error
            result.update_desc = f"Error fetching update: {str(e)}"

        self.log_finish()
        return result
