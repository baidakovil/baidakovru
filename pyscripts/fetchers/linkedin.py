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

    EVENT_TYPE_MAPPING = {
        'env_post': 'linkedin_post'  # post detected via environment variable
    }

    @require_config
    def fetch(self) -> FetchResult:
        """Fetch dummy LinkedIn data."""
        result = self.create_base_result()

        try:
            raw_date = getenv('LINKEDIN_LAST_UPDATE_DATE')
            if not raw_date:
                result.mark_as_error("LinkedIn update date not found in environment")
                return result

            result.raw_datetime, result.formatted_datetime = self.format_date(raw_date)
            result.update_url = f'www.linkedin.com/in/{self.config.username}'
            result.update_event = self.EVENT_TYPE_MAPPING['env_post']
            result.update_desc = "Update info at LinkedIn"
        except Exception as e:
            result.mark_as_error(f"Error processing LinkedIn data: {str(e)}")
            return result

        return result
