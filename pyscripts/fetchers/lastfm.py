from datetime import datetime

import requests

from ..config import FetcherConfig
from ..models import FetchResult
from .base import BaseFetcher, error_handler, require_config


class LastFMFetcher(BaseFetcher):
    @property
    def platform_id(self) -> str:
        return 'lastfm'

    def validate_config(self) -> bool:
        return bool(
            self.config.username and self.config.api_key and self.config.get_url()
        )

    EVENT_TYPE_MAPPING = {
        'api_scrobble': 'lastfm_scrobble'  # scrobble detected via API
    }

    @require_config
    @error_handler
    def fetch(self) -> FetchResult:
        """Fetch and parse latest Last.fm scrobbles."""
        url = self.config.get_url()
        response = requests.get(url)

        if response.status_code != 200:
            return self.create_error_result(
                f'Last.fm API error: {response.status_code}'
            )

        data = response.json()
        result = self.create_base_result(data)

        tracks = data.get('recenttracks', {}).get('track')
        if not tracks:
            return self.create_error_result('No tracks found in Last.fm response')

        return self._process_track(tracks[0])

    def _process_track(self, track: dict) -> FetchResult:
        """Process single track data."""
        result = self.create_base_result(track)

        if 'date' not in track:
            return self.create_error_result('No date information in track data')

        result.raw_datetime, result.formatted_datetime = self.format_date(
            track['date']['#text']
        )
        result.update_url = f"https://www.last.fm/user/{self.config.username}"
        result.update_event = self.EVENT_TYPE_MAPPING['api_scrobble']
        result.update_desc = "Listening to music"
        return result
