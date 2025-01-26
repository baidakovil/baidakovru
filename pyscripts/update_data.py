import os
from typing import List

from .config import config
from .database.dbmanager import DatabaseManager
from .fetchers.base import BaseFetcher
from .fetchers.github import GitHubFetcher
from .log_config import setup_logging

logger = setup_logging()


def get_fetchers() -> List[BaseFetcher]:
    fetchers = []

    if config.is_github_configured:
        fetchers.append(GitHubFetcher(config.github))

    # Add other fetchers similarly
    # if config.is_twitter_configured:
    #     fetchers.append(TwitterFetcher(config.twitter))

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
