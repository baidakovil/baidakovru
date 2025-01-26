from datetime import datetime

import requests

from ..config import FetcherConfig
from ..models import FetchResult
from .base import BaseFetcher


class LastFMFetcher(BaseFetcher):
    @property
    def platform_id(self) -> str:
        return 'lastfm'

    def validate_config(self) -> bool:
        if not self.config.username:
            self.logger.error("Last.fm username not configured")
            return False
        if not self.config.api_key:
            self.logger.error("Last.fm API key not configured")
            return False
        return True

    def fetch(self) -> FetchResult:
        """Fetch and parse latest Last.fm scrobbles."""
        self.log_start()

        if not self.validate_config():
            self.logger.error(f'Config for {self.platform_id} was not validated')
            return self.create_base_result()

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
                            result.raw_datetime = track_date
                            result.formatted_datetime = (
                                datetime.strptime(
                                    track_date, self.config.date_format['input']
                                )
                                .strftime(self.config.date_format['output'])
                                .lower()
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
