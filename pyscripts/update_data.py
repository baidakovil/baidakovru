import json
import logging
import os
import sqlite3

from pyscripts import log_config
from pyscripts.create_database import create_database_if_not_exists
from upscripts import github

logger = log_config.setup_logging()


def update_all_services():
    logger.info('Starting update all the services...')

    create_database_if_not_exists()

    # Подключаемся к базе данных
    db_path = os.path.join(os.path.dirname(__file__), '..', 'database.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Обновляем GitHub

    github_update = github.get_last_update('baidakovil')
    cursor.execute(
        '''
        INSERT OR REPLACE INTO services 
        (name, update_moment, raw_datetime, formatted_datetime, update_desc, raw_response) 
        VALUES (?, ?, ?, ?, ?, ?)
    ''',
        (
            'GitHub',
            github_update['update_moment'],
            github_update['raw_datetime'],
            github_update['formatted_datetime'],
            github_update['update_desc'],
            json.dumps(github_update['raw_response']),  # Convert to JSON string
        ),
    )

    conn.commit()
    conn.close()
    logger.info('Finishing update all the services...')
