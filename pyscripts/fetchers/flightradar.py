from datetime import datetime

import requests

from ..models import FetchResult
from .base import BaseFetcher, require_config


class FlightRadar24Fetcher(BaseFetcher):
    @property
    def platform_id(self) -> str:
        return 'flightradar'

    def validate_config(self) -> bool:
        return bool(self.config.username and self.config.get_url())

    @require_config
    def fetch(self) -> FetchResult:
        """Fetch and parse latest FlightRadar24 flight."""
        self.log_start()

        url = self.config.get_url()
        response = requests.get(url, headers=self.config.headers)
        result = self.create_base_result()

        if response.status_code == 200:
            html_content = response.text
            result.raw_response = html_content

            date_str = self._extract_last_date(html_content)
            if date_str:
                result.raw_datetime = date_str
                result.formatted_datetime = (
                    datetime.strptime(date_str, self.config.date_format['input'])
                    .strftime(self.config.date_format['output'])
                    .lower()
                )
                result.update_url = url
                result.update_desc = "New flight recorded"

        self.log_finish()
        return result

    def _extract_last_date(self, html_content: str) -> str:
        """Extract the date from the first flight entry."""
        # Normalize all whitespace and newlines to single spaces
        normalized_html = ' '.join(html_content.split())

        # Search for simplified pattern
        search_start = '<td class="flight-date">'
        search_end = '</span>'
        inner_date = '<span class="inner-date">'

        try:
            # Find the block containing our date
            start_idx = normalized_html.index(search_start)
            end_idx = normalized_html.index(search_end, start_idx) + len(search_end)
            date_block = normalized_html[start_idx:end_idx]

            # Extract the date from the block
            date_start = date_block.index(inner_date) + len(inner_date)
            date_str = date_block[date_start : date_block.index(search_end)]

            return date_str.strip()
        except ValueError:
            self.logger.error("Could not find date in FlightRadar24 page")
            return ""
