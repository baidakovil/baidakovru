from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional


@dataclass
class FetchResult:
    """Standardized container for storing fetched data from various platforms."""

    platform_id: str
    platform_name: str
    formatted_datetime: str  # Store as ISO 8601 format
    platform_url: Optional[str] = None
    update_desc: Optional[str] = None
    update_url: Optional[str] = None
    raw_response: Optional[Any] = None

    def __post_init__(self):
        # Ensure datetime is in ISO format
        if isinstance(self.formatted_datetime, datetime):
            self.formatted_datetime = self.formatted_datetime.isoformat()
