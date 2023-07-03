import uuid
from datetime import datetime, date
from dataclasses import dataclass, field
from typing import List, Any
import sqlite3
import os
from contextlib import contextmanager
from dotenv import load_dotenv
from psycopg2 import errors
load_dotenv()


@dataclass
class MixinId:
    id_: uuid.UUID = field(default_factory=uuid.uuid4)


@dataclass
class MixinDate:
    created: datetime = datetime.now()
    modified: datetime = datetime.now()


@dataclass
class FilmWork(MixinId, MixinDate):
    title: str = field(default="")
    creation_date: date = datetime.now()
    description: str = field(default="")
    rating: float = field(default=0.0)
    type_: str = field(default="")


@dataclass
class Person(MixinId, MixinDate):
    full_name: str = ''


def reformat_sqlite_fields(elem: dict) -> dict:
    """
        Создаем функцию осуществления замены по различающимся полям данным.
        Список необходим для расширения, в случае добавления новых данных.
    """
    if 'created_at' in elem.keys():
        elem['created'] = elem['created_at']
        del (elem['created_at'])

    if 'updated_at' in elem.keys():
        elem['modified'] = elem['updated_at']
        del (elem['updated_at'])

    if 'file_path' in elem.keys():
        del (elem['file_path'])

    if 'id' in elem.keys():
        elem['id_'] = elem['id']
        del elem['id']

    if 'type' in elem.keys():
        elem['type_'] = elem['type']
        del elem['type']
    return elem


def _prepare_data(cursor, row: list) -> dict:
    data = {}
    for index, column in enumerate(cursor.description):
        data[column[0]] = row[index]
    return data


class SQLiteExtractor:
    """
        Извлекаем данные из локального файла и упаковываем в словарь данных.
        Обрабатываем полученные данные в @dataclass в соответствие с типами.

    """

    def __init__(self, connection, package_limit: int):

        self.connection = connection
        self.package_limit = package_limit

    def load_sqlite(self, table: str) -> tuple:
        try:
            cursor = self.connection.cursor()

            cursor.row_factory = _prepare_data
            try:

                cursor.execute(f'SELECT * FROM {table}')
            except sqlite3.Error as e:
                raise e
            while True:
                rows = cursor.fetchmany(size=self.package_limit)

                if not rows:
                    return
                yield from rows
        except Exception as exception:
            print(exception)

    def format_dataclass_data(self, table: str, dataclass) -> List[Any]:
        data = self.load_sqlite(table)
        print(data)
        return [dataclass(**reformat_sqlite_fields(elem)) for elem in data]


datatables_list = {
    'film_work': FilmWork,
    #'person': Person,
    # 'person_film_work': PersonFilmWork,
    # 'genre': Genre,
    # 'genre_film_work': GenreFilmWork,
}


@contextmanager
def conn_context(db_path: str):
    sqlite_conn = sqlite3.connect(db_path)
    # sqlite_conn.row_factory = sqlite3.Row
    try:
        yield sqlite_conn
    finally:
        sqlite_conn.close()


if __name__ == '__main__':

    with conn_context(os.environ.get('SQLITE_DB_PATH')) as sqlite_connection:
        extract_data = []
        sqlite_extractor = SQLiteExtractor(sqlite_connection, 100)

        for base, schema in datatables_list.items():
            extract_data = sqlite_extractor.format_dataclass_data(base, schema)
            # postgres_saver.insert_data(base, extract_data, schema)
    print(extract_data)
#     postgres_saver.insert_data(base, extract_data, schema)
# # postgres_saver.insert_data(base, extract_data, schema)
# except Exception as exception:
#     print(exception)