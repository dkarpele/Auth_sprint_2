import logging
from functools import reduce
from dataclasses import astuple, fields

from psycopg2 import errors

# Get the logger specified in the file
logger = logging.getLogger(__name__)


class PostgresSaver:
    def __init__(self, connection):
        self.connection = connection

    def update_indexes(self, table_name, table_columns, index):
        with self.connection.cursor() as cursor:
            try:
                cursor.execute(f"""
                    SELECT indexdef FROM pg_indexes WHERE
                    tablename = '{table_name}' AND
                    indexname = '{index}';
                    """)

                index_def = cursor.fetchall()

                if not index_def:
                    cursor.execute(f"""
                        CREATE UNIQUE INDEX IF NOT EXISTS {index} ON
                        {table_name} {table_columns};
                        """)
                    logger.info(f'Index {index} created')
            except (errors.lookup("22P02"), errors.lookup("25P02")) as err:
                logger.error(err)

    def insert_data(self, base, extract_data, schema):
        table_columns = ', '.join(i.name for i in fields(schema))
        repl = ("id_", "id"), ("type_", "type")
        table_columns = reduce(lambda a, kv: a.replace(*kv), repl,
                               table_columns)

        values_temp = f"({'%s, ' * len((fields(schema)))}"[:-2] + ")"
        with self.connection.cursor() as cursor:
            args = ''
            for item in extract_data:
                for i in fields(item):
                    if i.name == 'created':
                        item.created = 'NOW()'
                    if i.name == 'modified':
                        item.modified = 'NOW()'
                item = cursor.mogrify(values_temp, astuple(item)).\
                    decode().replace("'NOW()'", "NOW()")
                args += item + ','
            args = args[:-1]
            try:
                cursor.execute(f"""
                    INSERT INTO {base} ({table_columns})
                    VALUES {args}
                    ON CONFLICT (id) DO NOTHING;
                    """)
                logger.info(f'Migration {base} finished successfully.')
            except (errors.lookup("22P02"), errors.lookup("25P02")) as err:
                logger.error(err)
