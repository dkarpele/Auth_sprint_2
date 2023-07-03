from typing import List, Any

import sqlite3
import logging

# Get the logger specified in the file
logger = logging.getLogger(__name__)


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
            logger.error(exception)

    def format_dataclass_data(self, table: str, dataclass) -> List[Any]:
        data = self.load_sqlite(table)
        return [dataclass(**reformat_sqlite_fields(elem)) for elem in data]
