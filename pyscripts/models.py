from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional


@dataclass
class FetchResult:
    """Standardized container for storing fetched data from various platforms."""

    platform_id: str
    platform_name: str
    raw_response: Optional[Any] = None
    raw_datetime: Optional[str] = None
    formatted_datetime: Optional[str] = None
    update_desc: Optional[str] = None
    update_event: Optional[str] = None
    update_url: Optional[str] = None
    platform_url: Optional[str] = None
    is_error: bool = False

    def __post_init__(self):
        # Ensure datetime is in ISO format
        if isinstance(self.formatted_datetime, datetime):
            self.formatted_datetime = self.formatted_datetime.isoformat()

    def mark_as_error(self, error_desc: str):
        """Mark result as error with description."""
        self.is_error = True
        self.update_desc = f"Error: {error_desc}"
        self.update_event = None
