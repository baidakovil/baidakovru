from datetime import datetime

import requests

from ..config import FetcherConfig
from ..fetchers.base import BaseFetcher, require_config
from ..models import FetchResult


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
    def fetch(self) -> FetchResult:
        """Fetch and parse latest Last.fm scrobbles."""
        self.log_start()

        url = self.config.get_url()
        try:
            response = requests.get(url)
            result = self.create_base_result()

            if response.status_code == 200:
                data = response.json()
                result.raw_response = data

                try:
                    if data.get('recenttracks', {}).get('track'):
                        result = self._process_track(data['recenttracks']['track'][0])
                except Exception as e:
                    result.mark_as_error(f"Error parsing Last.fm response: {str(e)}")
                    return result
            else:
                result.mark_as_error(f'Last.fm API error: {response.status_code}')
                return result

        except Exception as e:
            self.logger.error(f'Error fetching from Last.fm: {e}')
            result = self.create_base_result({'error': str(e)})
            result.update_desc = f"Error fetching update: {str(e)}"

        self.log_finish()
        return result

    def _process_track(self, track: dict) -> FetchResult:
        """Process single track data."""
        result = self.create_base_result()
        if 'date' in track:
            result.raw_datetime, result.formatted_datetime = self.format_date(
                track['date']['#text']
            )
            result.update_url = f"https://www.last.fm/user/{self.config.username}"
            result.update_event = self.EVENT_TYPE_MAPPING['api_scrobble']
            result.update_desc = "Listening to music"
        return result
