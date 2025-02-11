import os
from typing import List

from .config import config
from .database.dbmanager import DatabaseManager
from .fetchers.base import BaseFetcher
from .fetchers.flightradar import FlightRadar24Fetcher
from .fetchers.github import GitHubFetcher
from .fetchers.inat import INatFetcher
from .fetchers.lastfm import LastFMFetcher
from .fetchers.linkedin import LinkedInFetcher
from .fetchers.telegram import TelegramFetcher
from .log_config import setup_logging

logger = setup_logging()


def get_fetchers() -> List[BaseFetcher]:
    """Get list of configured fetchers."""
    logger.info("Starting fetcher configuration...")

    # Create all fetchers
    all_fetchers = [
        GitHubFetcher(config.github),
        INatFetcher(config.inat),
        TelegramFetcher(config.telegram),
        LastFMFetcher(config.lastfm),
        LinkedInFetcher(config.linkedin),
        FlightRadar24Fetcher(config.flightradar),
    ]

    # Filter only properly configured fetchers and log unconfigured ones
    configured_fetchers = []
    for fetcher in all_fetchers:
        if fetcher.validate_config():
            configured_fetchers.append(fetcher)
        else:
            logger.warning(
                f"Fetcher {fetcher.platform_id} ({type(fetcher).__name__}) is not properly configured"
            )

    if not configured_fetchers:
        logger.warning("No fetchers were properly configured")
    else:
        logger.info(
            f"Successfully configured {len(configured_fetchers)}/{len(all_fetchers)} fetchers: "
            f"{[type(f).__name__ for f in configured_fetchers]}"
        )

    return configured_fetchers


def update_all_platforms():
    logger.info("Starting update for all platforms...")

    db_manager = DatabaseManager(config.db_path)

    if not db_manager.health_check():
        logger.error("Database health check failed. Skipping updates.")
        return

    fetchers = get_fetchers()
    if not fetchers:
        logger.warning("No fetchers were configured. Check your configuration.")
        return

    for fetcher in fetchers:
        logger.info(f"Processing fetcher: {type(fetcher).__name__}")
        result = fetcher.fetch()
        db_manager.update_platform_data(result)
        logger.info(f"Successfully updated data for {fetcher.platform_id}")

    logger.info("Finished updating all platforms")
