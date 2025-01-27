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
    update_url: Optional[str] = None
    update_moment: str = field(
        default_factory=lambda: datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    )
