from datetime import datetime

import requests

from ..config import FetcherConfig
from ..models import FetchResult
from .base import BaseFetcher, require_config


class INatFetcher(BaseFetcher):
    @property
    def platform_id(self) -> str:
        return 'inat'

    def validate_config(self) -> bool:
        return bool(self.config.username and self.config.get_url())

    @require_config
    def fetch(self) -> FetchResult:
        """Fetch and parse latest iNaturalist observations."""
        self.log_start()

        url = self.config.get_url()
        try:
            response = requests.get(url, headers=self.config.headers)
            result = self.create_base_result()

            if response.status_code == 200:
                data = response.json()
                result.raw_response = data

                try:
                    if data.get('results') and len(data['results']) > 0:
                        latest_observation = data['results'][0]
                        created_at = latest_observation['created_at']

                        if '+' in created_at or '-' in created_at:
                            created_at = created_at[:-3] + created_at[-2:]

                        result.raw_datetime = created_at
                        result.formatted_datetime = (
                            datetime.strptime(
                                created_at, self.config.date_format['input']
                            )
                            .strftime(self.config.date_format['output'])
                            .lower()
                        )

                        species_name = latest_observation.get(
                            'species_guess', 'Unknown species'
                        )
                        place_name = latest_observation.get(
                            'place_guess', 'unknown location'
                        )
                        result.update_url = f"https://www.inaturalist.org/observations/{latest_observation.get('id')}"
                        result.update_desc = (
                            f"Observation of {species_name} at {place_name}"
                        )
                except Exception as e:
                    self.logger.error(f'Error parsing iNat response: {e}')
                    result.update_desc = f"Error parsing update: {str(e)}"

            elif response.status_code == 404:
                self.logger.error(
                    f'404 when fetching from iNat for {self.config.username}'
                )
                result.raw_response = {'error': 'Not Found', 'status': 404}
            else:
                self.logger.error(f'Error status from iNat: {response.status_code}')
                result.raw_response = {
                    'error': 'Bad Response',
                    'status': response.status_code,
                }

        except Exception as e:
            self.logger.error(f'Error fetching from iNat: {e}')
            result = self.create_base_result({'error': str(e)})
            result.update_desc = f"Error fetching update: {str(e)}"

        self.log_finish()
        return result
