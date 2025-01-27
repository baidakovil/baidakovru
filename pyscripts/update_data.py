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
    fetchers = []
    logger.info("Starting fetcher configuration...")

    if config.is_github_configured:
        fetchers.append(GitHubFetcher(config.github))

    if config.is_inat_configured:
        fetchers.append(INatFetcher(config.inat))

    if config.is_telegram_configured:
        fetchers.append(TelegramFetcher(config.telegram))

    if config.is_lastfm_configured:
        fetchers.append(LastFMFetcher(config.lastfm))

    if config.is_linkedin_configured:
        fetchers.append(LinkedInFetcher(config.linkedin))

    if config.is_flightradar_configured:
        fetchers.append(FlightRadar24Fetcher(config.flightradar))

    logger.info(
        f"Configured {len(fetchers)} fetchers: {[type(f).__name__ for f in fetchers]}"
    )
    return fetchers


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
        try:
            logger.debug(f"Starting fetch for {fetcher.platform_id}")
            result = fetcher.fetch()
            logger.debug(
                f"Successfully fetched data for {fetcher.platform_id}, updating database"
            )
            db_manager.update_platform_data(result)
            logger.info(f"Successfully updated data for {fetcher.platform_id}")
        except Exception as e:
            logger.error(
                f"Error updating {fetcher.platform_id}: {str(e)}", exc_info=True
            )

    logger.info("Finished updating all platforms")
