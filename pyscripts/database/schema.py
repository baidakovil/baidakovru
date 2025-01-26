"""Database schema and initialization functions."""

SCHEMA_VERSION = 1

CREATE_TABLES_SQL = {
    'schema_version': """
        CREATE TABLE IF NOT EXISTS schema_version (
            version INTEGER PRIMARY KEY
        )
    """,
    'updates': '''
        CREATE TABLE IF NOT EXISTS updates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            platform_id TEXT NOT NULL,
            platform_name TEXT NOT NULL,
            formatted_datetime TEXT,
            update_desc TEXT,
            update_moment TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''',
}
