import logging
import os
import sqlite3

from pyscripts import log_config

logger = log_config.setup_logging()


def create_database_if_not_exists():
    logger.debug('Начинается проверка существования базы данных...')
    db_path = os.path.join(os.path.dirname(__file__), 'services.db')
    if not os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        cursor.execute(
            '''
            CREATE TABLE IF NOT EXISTS services (
                name TEXT PRIMARY KEY,
                update_moment DATETIME,
                raw_datetime TEXT,
                formatted_datetime DATETIME,
                update_desc TEXT,
                raw_response TEXT
            )
            '''
        )

        conn.commit()
        conn.close()
        logger.info('База данных создана')
    else:
        logger.info('База данных уже существует')


if __name__ == "__main__":
    logger.info("Condition if __name__ == __main__ satisfied: creating database...")
    create_database_if_not_exists()
