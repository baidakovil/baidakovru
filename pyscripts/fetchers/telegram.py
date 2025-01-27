from datetime import datetime

import requests

from ..config import FetcherConfig
from ..models import FetchResult
from .base import BaseFetcher


class TelegramFetcher(BaseFetcher):
    @property
    def platform_id(self) -> str:
        return 'tg'

    def validate_config(self) -> bool:
        if not self.config.username:
            self.logger.error("Telegram username not configured")
            return False
        if not self.config.get_url():
            self.logger.error("Telegram URL configuration is invalid")
            return False
        return True

    def _extract_last_date(self, html_content: str) -> str:
        """Extract the date from the last message in the channel."""
        search_str = '<time datetime="'
        date_end = '"'

        try:
            last_idx = html_content.rindex(search_str)
            date_start = last_idx + len(search_str)
            date_end_idx = html_content.index(date_end, date_start)
            return html_content[date_start:date_end_idx]
        except ValueError:
            self.logger.error("Could not find date in Telegram page")
            return ""

    def _extract_message_url(self, html_content: str) -> str:
        """Extract the URL from the last message."""
        search_str = 'tgme_widget_message_date" href="'
        url_end = '">'

        try:
            last_idx = html_content.rindex(search_str)
            url_start = last_idx + len(search_str)
            url_end_idx = html_content.index(url_end, url_start)
            return html_content[url_start:url_end_idx]
        except ValueError:
            self.logger.error("Could not find message URL in Telegram page")
            return ""

    def fetch(self) -> FetchResult:
        """Fetch and parse latest Telegram channel message."""
        self.log_start()

        if not self.validate_config():
            self.logger.error(
                f'Config for {self.platform_id} was not validated. Returning empty result.'
            )
            return self.create_base_result()

        url = self.config.get_url()
        response = requests.get(url, headers=self.config.headers)
        result = self.create_base_result()

        if response.status_code == 200:
            html_content = response.text
            result.raw_response = html_content

            date_str = self._extract_last_date(html_content)
            if date_str:
                # Convert timezone format from "+03:00" to "+0300" for proper parsing
                if '+' in date_str or '-' in date_str:
                    date_str = date_str[:-3] + date_str[-2:]

                result.raw_datetime = date_str
                result.formatted_datetime = (
                    datetime.strptime(date_str, self.config.date_format['input'])
                    .strftime(self.config.date_format['output'])
                    .lower()
                )
                result.update_url = self._extract_message_url(html_content)
                result.update_desc = "New message in Telegram channel"

        elif response.status_code == 404:
            self.logger.error(
                f'404 when fetching updates from Telegram for {self.config.username}'
            )
        else:
            self.logger.error(
                f'Error when fetching updates from Telegram for {self.config.username}: {response.status_code}'
            )

        self.log_finish()
        return result
