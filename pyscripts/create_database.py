import os
import sqlite3

from dotenv import load_dotenv

from pyscripts import log_config

load_dotenv()
DB_PATH = os.getenv('DB_PATH')

logger = log_config.setup_logging()


def create_database_if_not_exists():
    logger.debug('Начинается проверка существования базы данных...')
    if not os.path.exists(DB_PATH):
        conn = sqlite3.connect(DB_PATH)
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
