import os
import psycopg2
import sqlite3

from psycopg2.extras import DictCursor
from dotenv import load_dotenv
from contextlib import contextmanager

load_dotenv()
dsl = {'dbname': os.environ.get('DB_NAME'),
       'user': os.environ.get('DB_USER'),
       'password': os.environ.get('DB_PASSWORD'),
       'host': os.environ.get('DB_HOST', '127.0.0.1'),
       'port': os.environ.get('DB_PORT', 5432),
       'options': '-c search_path=%s' % os.environ.get('PG_SCHEMA')}


@contextmanager
def conn_context(db_path: str):
    sqlite_conn = sqlite3.connect(db_path)
    yield sqlite_conn
    sqlite_conn.close()


def prepare_query(query):
    with conn_context(os.environ.get('SQLITE_DB_PATH')) as sqlite_connection, \
            psycopg2.connect(**dsl,
                             cursor_factory=DictCursor) as pg_connection:
        curs_sqlite = sqlite_connection.cursor()
        curs_sqlite.execute(query)
        data_sqlite = curs_sqlite.fetchall()

        curs_pg = pg_connection.cursor()
        curs_pg.execute(query)
        data_pg = curs_pg.fetchall()
        return data_sqlite, data_pg


def test_integrity():
    query = "select " \
            "(select count(*) from person) person,"\
            "(select count(*) from genre) genre, "\
            "(select count(*) from film_work) film_work, "\
            "(select count(*) from genre_film_work) genre_film_work, "\
            "(select count(*) from person_film_work) person_film_work"
    data_sqlite = prepare_query(query)[0]
    data_pg = prepare_query(query)[1]
    assert list(data_sqlite[0]) == list(data_pg[0])


def test_consistency():
    genre_query = "select id, name, description from genre"
    data_sqlite = prepare_query(genre_query)[0]
    data_pg = prepare_query(genre_query)[1]
    assert list(data_sqlite[0]) == list(data_pg[0])

    film_work_query = "select id, title, description, creation_date, " \
                      "rating, type from film_work"
    data_sqlite = prepare_query(film_work_query)[0]
    data_pg = prepare_query(film_work_query)[1]
    assert list(data_sqlite[0]) == list(data_pg[0])

    person_query = "select id, full_name from person"
    data_sqlite = prepare_query(person_query)[0]
    data_pg = prepare_query(person_query)[1]
    assert list(data_sqlite[0]) == list(data_pg[0])

    genre_film_work_query = "select id, genre_id, film_work_id " \
                            "from genre_film_work"
    data_sqlite = prepare_query(genre_film_work_query)[0]
    data_pg = prepare_query(genre_film_work_query)[1]
    assert list(data_sqlite[0]) == list(data_pg[0])

    person_film_work_query = "select id, person_id, film_work_id, role " \
                             "from person_film_work"
    data_sqlite = prepare_query(person_film_work_query)[0]
    data_pg = prepare_query(person_film_work_query)[1]
    assert list(data_sqlite[0]) == list(data_pg[0])
