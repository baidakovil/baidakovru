from datetime import datetime

import requests

from ..config import FetcherConfig
from ..models import FetchResult
from .base import BaseFetcher, error_handler, require_config


class INatFetcher(BaseFetcher):
    @property
    def platform_id(self) -> str:
        return 'inat'

    def validate_config(self) -> bool:
        return bool(self.config.username and self.config.get_url())

    EVENT_TYPE_MAPPING = {
        'api_observation': 'inat_observation'  # observation detected via API
    }

    @require_config
    @error_handler
    def fetch(self) -> FetchResult:
        """Fetch and parse latest iNaturalist observations."""
        url = self.config.get_url()
        response = requests.get(url, headers=self.config.headers)

        if response.status_code != 200:
            return self.create_error_result(f'iNat API error: {response.status_code}')

        data = response.json()
        result = self.create_base_result(data)

        if not data.get('results') or len(data['results']) == 0:
            return self.create_error_result('No observations found in iNat response')

        latest_observation = data['results'][0]
        return self._process_observation(latest_observation)

    def _process_observation(self, observation: dict) -> FetchResult:
        """Process single iNaturalist observation."""
        result = self.create_base_result(observation)

        created_at = observation['created_at']
        if '+' in created_at or '-' in created_at:
            created_at = created_at[:-3] + created_at[-2:]

        result.raw_datetime, result.formatted_datetime = self.format_date(created_at)

        species_name = observation.get('species_guess', 'Unknown species')
        place_name = observation.get('place_guess', 'unknown location')

        result.update_url = (
            f"https://www.inaturalist.org/observations/{observation.get('id')}"
        )
        result.update_event = self.EVENT_TYPE_MAPPING['api_observation']
        result.update_desc = f"Observation of {species_name} at {place_name}"

        return result
