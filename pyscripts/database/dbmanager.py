import json
import os
import sqlite3
from typing import Optional

from ..log_config import setup_logging
from ..models import FetchResult
from .schema import CREATE_TABLES_SQL, SCHEMA_VERSION

logger = setup_logging()


class DatabaseManager:
    """Manages database operations for storing fetched platform data."""

    def __init__(self, db_path: str):
        """Initialize database manager and ensure database exists."""
        self.db_path = db_path
        self.logger = logger
        self._ensure_database_exists()

    def _ensure_database_exists(self) -> None:
        """Create database and tables if they don't exist."""
        db_dir = os.path.dirname(os.path.abspath(self.db_path))
        os.makedirs(db_dir, exist_ok=True)

        try:
            with sqlite3.connect(self.db_path) as conn:
                # Create all tables
                for table_sql in CREATE_TABLES_SQL.values():
                    conn.execute(table_sql)

                # Check/update schema version
                cur = conn.cursor()
                cur.execute("SELECT version FROM schema_version")
                result = cur.fetchone()

                if not result:
                    # New database, insert version
                    cur.execute(
                        "INSERT INTO schema_version (version) VALUES (?)",
                        (SCHEMA_VERSION,),
                    )
                    conn.commit()
                elif result[0] != SCHEMA_VERSION:
                    # TODO: Implement migration logic if needed
                    self.logger.warning(
                        f"Database schema version mismatch: {result[0]} != {SCHEMA_VERSION}"
                    )

        except sqlite3.Error as e:
            self.logger.error(f"Database initialization error: {e}")
            raise

    def health_check(self) -> bool:
        """Verify database exists and is accessible."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cur = conn.cursor()

                # Check SQLite version
                cur.execute('SELECT sqlite_version()')
                version = cur.fetchone()[0]
                self.logger.info(f"SQLite version: {version}")

                # Check Python's sqlite3 version
                sqlite_version = sqlite3.sqlite_version
                self.logger.info(f"Python sqlite3 version: {sqlite_version}")

                cur.execute("SELECT version FROM schema_version")
                return bool(cur.fetchone())
        except sqlite3.Error as e:
            self.logger.error(f"Database health check failed: {e}")
            return False

    def update_platform_data(self, result: FetchResult):
        if not result:
            return

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO updates 
                (platform_id, platform_name, formatted_datetime, update_desc, 
                 update_event, update_url, platform_url, raw_response)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    result.platform_id,
                    result.platform_name,
                    result.formatted_datetime,
                    result.update_desc,
                    result.update_event,
                    result.update_url,
                    result.platform_url,
                    json.dumps(result.raw_response) if result.raw_response else None,
                ),
            )
            conn.commit()

    def get_connection(self):
        """Get a database connection."""
        return sqlite3.connect(self.db_path)

    def close_all(self):
        """Close any remaining connections (for cleanup)."""
        # SQLite connections are automatically closed,
        # but we keep this method for future connection pooling
        pass
