"""Preview/apply the Flashcards migration without importing the application."""
import argparse
from datetime import datetime, timezone
from pathlib import Path
import sqlite3

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.engine import make_url

TABLES = ('flashcard_progress', 'flashcards', 'flashcard_sets')
MIGRATION = Path(__file__).resolve().parents[1] / 'migrations/20261002_remove_flashcards.sql'


def migrate(database_url: str, apply: bool = False):
    url = make_url(database_url)
    if url.get_backend_name() not in ('sqlite', 'postgresql'):
        raise ValueError('Only SQLite and PostgreSQL are supported')
    sqlite_path = None
    if url.get_backend_name() == 'sqlite':
        sqlite_path = Path(url.database or '').resolve()
        if not sqlite_path.is_file():
            raise ValueError('The SQLite database must already exist')

    engine = create_engine(url)
    try:
        with engine.connect() as connection:
            inspector = inspect(connection)
            existing = inspector.get_table_names()
            for table in existing:
                if table not in TABLES:
                    for key in inspector.get_foreign_keys(table):
                        if key['referred_table'] in TABLES:
                            raise ValueError(f'{table} still references {key["referred_table"]}')
            counts = {
                table: connection.execute(text(f'SELECT COUNT(*) FROM {table}')).scalar_one()
                for table in TABLES if table in existing
            }
        for table, count in counts.items():
            print(f'{table}: {count} rows')
        if not apply:
            print('Preview only. Use --apply after reviewing the target and backup.')
            return counts
        if sqlite_path and counts:
            stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
            backup = sqlite_path.with_name(f'{sqlite_path.name}.before-flashcard-removal-{stamp}.bak')
            with sqlite3.connect(sqlite_path.as_uri() + '?mode=ro', uri=True) as source:
                with sqlite3.connect(backup) as destination:
                    source.backup(destination)
            print(f'Backup: {backup.name}')
        statements = '\n'.join(
            line for line in MIGRATION.read_text().splitlines()
            if not line.lstrip().startswith('--')
        )
        with engine.begin() as connection:
            if sqlite_path:
                connection.exec_driver_sql('PRAGMA foreign_keys = ON')
                # SQLite DDL needs an explicit transaction for rollback.
                connection.exec_driver_sql('BEGIN IMMEDIATE')
            for statement in statements.split(';'):
                if statement.strip():
                    connection.execute(text(statement))
        print('Flashcard tables removed. Other tables unchanged.')
        return counts
    finally:
        engine.dispose()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--database-url', required=True, help='Explicit target; never reads .env')
    parser.add_argument('--apply', action='store_true', help='Delete the three Flashcard tables')
    args = parser.parse_args()
    migrate(args.database_url, args.apply)
