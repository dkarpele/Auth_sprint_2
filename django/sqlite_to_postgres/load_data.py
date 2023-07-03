import os
import sqlite3
import logging.config
from contextlib import contextmanager

import psycopg2
from psycopg2.extensions import connection as _connection
from psycopg2.extras import DictCursor
from dotenv import load_dotenv

from extractor import SQLiteExtractor
from saver import PostgresSaver
from schemas import FilmWork, Genre, Person, GenreFilmWork, PersonFilmWork

logging.config.fileConfig(fname='logger.conf', disable_existing_loggers=False)

# Get the logger specified in the file
logger = logging.getLogger(__name__)

load_dotenv()

datatables_list = {
    'film_work': FilmWork,
    'person': Person,
    'person_film_work': PersonFilmWork,
    'genre': Genre,
    'genre_film_work': GenreFilmWork,
}


def load_from_sqlite(sqlite_conn: sqlite3.Connection, pg_conn: _connection):
    """Основной метод загрузки данных из SQLite в Postgres"""
    logger.info('Starting the migration...')

    sqlite_extractor = SQLiteExtractor(sqlite_conn,
                                       int(os.environ.get('SIZE', 100)))

    postgres_saver = PostgresSaver(pg_conn)
    postgres_saver.update_indexes('genre_film_work',
                                  '(film_work_id, genre_id)',
                                  'film_work_genre')
    postgres_saver.update_indexes('person_film_work',
                                  '(film_work_id, person_id, role)',
                                  'film_work_person_role')

    for base, schema in datatables_list.items():
        extract_data = sqlite_extractor.format_dataclass_data(base, schema)
        postgres_saver.insert_data(base, extract_data, schema)


if __name__ == '__main__':
    dsl = {'dbname': os.environ.get('DB_NAME'),
           'user': os.environ.get('DB_USER'),
           'password': os.environ.get('DB_PASSWORD'),
           'host': os.environ.get('DB_HOST', '127.0.0.1'),
           'port': os.environ.get('DB_PORT', 5432),
           'options': '-c search_path=%s' % os.environ.get('PG_SCHEMA')}

    @contextmanager
    def conn_context(db_path: str):
        sqlite_conn = sqlite3.connect(db_path)
        try:
            yield sqlite_conn
        finally:
            sqlite_conn.close()

    pg_connection = psycopg2.connect(**dsl, cursor_factory=DictCursor)

    try:
        with conn_context(os.environ.get('SQLITE_DB_PATH')) as \
                sqlite_connection, pg_connection:
            load_from_sqlite(sqlite_connection, pg_connection)
    except Exception as err:
        logger.error(err)
    finally:
        pg_connection.close()
