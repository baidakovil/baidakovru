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
                        latest_track = data['recenttracks']['track'][0]
                        if 'date' in latest_track:
                            track_date = latest_track['date']['#text']
                            result.raw_datetime, result.formatted_datetime = (
                                self.format_date(track_date)
                            )
                            result.update_url = (
                                f"https://www.last.fm/user/{self.config.username}"
                            )
                            result.update_desc = "Listening to music"

                except Exception as e:
                    self.logger.error(f'Error parsing Last.fm response: {e}')
                    result.update_desc = f"Error parsing update: {str(e)}"

            else:
                self.logger.error(f'Error status from Last.fm: {response.status_code}')
                result.raw_response = {
                    'error': 'Bad Response',
                    'status': response.status_code,
                }

        except Exception as e:
            self.logger.error(f'Error fetching from Last.fm: {e}')
            result = self.create_base_result({'error': str(e)})
            result.update_desc = f"Error fetching update: {str(e)}"

        self.log_finish()
        return result
