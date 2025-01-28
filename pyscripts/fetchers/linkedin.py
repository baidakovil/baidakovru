from datetime import datetime
from os import getenv

from ..models import FetchResult
from .base import BaseFetcher, require_config


class LinkedInFetcher(BaseFetcher):
    @property
    def platform_id(self) -> str:
        return 'linkedin'

    def validate_config(self) -> bool:
        return bool(self.config.username and getenv('LINKEDIN_LAST_UPDATE_DATE'))

    @require_config
    def fetch(self) -> FetchResult:
        """Fetch dummy LinkedIn data."""
        self.log_start()
        result = self.create_base_result()

        result.raw_datetime = getenv('LINKEDIN_LAST_UPDATE_DATE')
        result.formatted_datetime = (
            datetime.strptime(result.raw_datetime, self.config.date_format['input'])
            .strftime(self.config.date_format['output'])
            .lower()
        )
        result.update_url = f'www.linkedin.com/in/{self.config.username}'
        result.update_desc = "Update info at LinkedIn"

        self.log_finish()
        return result
