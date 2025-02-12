from abc import ABC, abstractmethod
from datetime import datetime
from functools import wraps
from typing import Tuple

import pytz

from ..config import FetcherConfig
from ..log_config import setup_logging
from ..models import FetchResult

logger = setup_logging()


def require_config(f):
    """Decorator to check if fetcher is properly configured before fetching."""

    @wraps(f)
    def wrapper(self, *args, **kwargs):
        if not self.validate_config():
            self.logger.warning(
                f'Fetcher {self.platform_id} is not properly configured'
            )
            return self.create_base_result({'error': 'Fetcher not configured'})
        return f(self, *args, **kwargs)

    return wrapper


def error_handler(f):
    """Decorator to handle logging and error handling for fetchers."""

    @wraps(f)
    def wrapper(self, *args, **kwargs):
        self.log_start()
        try:
            result = f(self, *args, **kwargs)
            return result
        except Exception as e:
            error_msg = f'Error fetching from {self.platform_id}: {str(e)}'
            self.logger.error(error_msg)
            return self.create_error_result(error_msg)
        finally:
            self.log_finish()

    return wrapper


class BaseFetcher(ABC):
    """Abstract base class defining the contract for all platform fetchers."""

    def __init__(self, config: FetcherConfig):
        """Initialize fetcher with platform-specific configuration."""
        self.config = config
        self.logger = logger

    @property
    @abstractmethod
    def platform_id(self) -> str:
        """Return unique identifier for the platform."""
        pass

    def create_base_result(self, raw_response=None) -> FetchResult:
        """Create base result with platform info and raw response."""
        return FetchResult(
            platform_id=self.platform_id,
            platform_name=self.config.platform_name,
            raw_response=raw_response,
            platform_url=self.config.platform_url,
        )

    def create_error_result(self, error_message: str) -> FetchResult:
        """Create standardized error result."""
        result = self.create_base_result()
        result.mark_as_error(error_message)
        return result

    def format_date(self, date_str: str) -> Tuple[str, str]:
        """
        Format date string using config formats.
        Returns tuple of (raw_datetime, formatted_datetime).
        """
        try:
            # Parse the date string with the input format
            dt = datetime.strptime(date_str, self.config.date_format['input'])
            # Convert to UTC
            dt = dt.astimezone(pytz.utc)
            # Format the date string with the output format
            return date_str, dt.strftime(self.config.date_format['output']).lower()
        except (ValueError, AttributeError) as e:
            self.logger.error(f'Failed to parse date {date_str}: {e}')
            return date_str, None

    @abstractmethod
    @error_handler
    def fetch(self) -> FetchResult:
        """Implementation of fetch operation by concrete fetchers."""
        pass

    @abstractmethod
    def validate_config(self) -> bool:
        """Verify that all required configuration values are present."""
        pass

    def log_start(self):
        """Log the start of fetch operation."""
        self.logger.info(f'Starting update for {self.platform_id} platform...')

    def log_finish(self):
        """Log the completion of fetch operation."""
        self.logger.info(f'Finishing update for {self.platform_id} platform...')
