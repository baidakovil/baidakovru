from datetime import datetime

import requests

from ..models import FetchResult
from .base import BaseFetcher, error_handler, require_config


class FlightRadar24Fetcher(BaseFetcher):
    @property
    def platform_id(self) -> str:
        return 'flightradar'

    def validate_config(self) -> bool:
        return bool(self.config.username and self.config.get_url())

    EVENT_TYPE_MAPPING = {
        'html_flight': 'fr24_flight'  # flight detected via HTML scraping
    }

    @require_config
    @error_handler
    def fetch(self) -> FetchResult:
        """Fetch and parse latest FlightRadar24 flight."""
        url = self.config.get_url()
        response = requests.get(url, headers=self.config.headers)

        if response.status_code != 200:
            return self.create_error_result(
                f'FlightRadar24 error: {response.status_code}'
            )

        html_content = response.text
        result = self.create_base_result(html_content)

        date_str = self._extract_last_date(html_content)
        if not date_str:
            return self.create_error_result("Could not find date in FlightRadar24 page")

        return self._process_flight(html_content, date_str)

    def _extract_last_date(self, html_content: str) -> str:
        """Extract the date from the first flight entry."""
        normalized_html = ' '.join(html_content.split())
        search_start = '<td class="flight-date">'
        search_end = '</span>'
        inner_date = '<span class="inner-date">'

        start_idx = normalized_html.index(search_start)
        end_idx = normalized_html.index(search_end, start_idx) + len(search_end)
        date_block = normalized_html[start_idx:end_idx]

        date_start = date_block.index(inner_date) + len(inner_date)
        date_str = date_block[date_start : date_block.index(search_end)]

        return date_str.strip()

    def _process_flight(self, html_content: str, date_str: str) -> FetchResult:
        """Process flight data."""
        result = self.create_base_result(html_content)
        result.raw_datetime, result.formatted_datetime = self.format_date(date_str)
        result.update_url = self.config.get_url()
        result.update_event = self.EVENT_TYPE_MAPPING['html_flight']
        result.update_desc = "New flight recorded"
        return result
