from datetime import datetime
from os import getenv

from ..models import FetchResult
from .base import BaseFetcher, error_handler, require_config


class LinkedInFetcher(BaseFetcher):
    @property
    def platform_id(self) -> str:
        return 'linkedin'

    def validate_config(self) -> bool:
        return bool(self.config.username and getenv('LINKEDIN_LAST_UPDATE_DATE'))

    EVENT_TYPE_MAPPING = {
        'env_post': 'linkedin_post'  # post detected via environment variable
    }

    @require_config
    @error_handler
    def fetch(self) -> FetchResult:
        """Fetch dummy LinkedIn data."""
        raw_date = getenv('LINKEDIN_LAST_UPDATE_DATE')
        if not raw_date:
            return self.create_error_result(
                "LinkedIn update date not found in environment"
            )

        result = self.create_base_result()
        result.raw_datetime, result.formatted_datetime = self.format_date(raw_date)
        result.update_url = f'www.linkedin.com/in/{self.config.username}'
        result.update_event = self.EVENT_TYPE_MAPPING['env_post']
        result.update_desc = "Update info at LinkedIn"
        return result
