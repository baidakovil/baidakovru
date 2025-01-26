import os
from typing import List

from .config import config
from .database.dbmanager import DatabaseManager
from .fetchers.base import BaseFetcher
from .fetchers.github import GitHubFetcher
from .fetchers.inat import INatFetcher
from .fetchers.lastfm import LastFMFetcher
from .fetchers.telegram import TelegramFetcher
from .log_config import setup_logging

logger = setup_logging()


def get_fetchers() -> List[BaseFetcher]:
    fetchers = []

    if config.is_github_configured:
        fetchers.append(GitHubFetcher(config.github))

    if config.is_inat_configured:
        fetchers.append(INatFetcher(config.inat))

    if config.is_telegram_configured:
        fetchers.append(TelegramFetcher(config.telegram))

    if config.is_lastfm_configured:
        fetchers.append(LastFMFetcher(config.lastfm))

    return fetchers


def update_all_platforms():
    logger.info("Starting update for all platforms...")

    db_manager = DatabaseManager(config.db_path)

    if not db_manager.health_check():
        logger.error("Database health check failed. Skipping updates.")
        return

    for fetcher in get_fetchers():
        try:
            result = fetcher.fetch()
            db_manager.update_platform_data(result)
        except Exception as e:
            logger.error(f"Error updating {fetcher.platform_id}: {e}")

    logger.info("Finished updating all platforms")
