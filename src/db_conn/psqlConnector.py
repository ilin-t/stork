import os
import re
from pathlib import Path

import cchardet as chardet

import psycopg2
from configparser import ConfigParser
import time

import pandas as pd

from psycopg2 import sql, extras


class PsqlConnector:
    def __init__(self, config_path):
        self.db_config = {}
        self.logger = None
        self.config_path = config_path
        self.connection = None
        self.cursor = None
        self.schema_map = {"object": "varchar", "int64": "bigint", "int8": "smallint", "int16": "smallint",
                           "int32": "integer", "uint8": "smallint",
                           "uint16": "smallint", "uint32": "integer", "uint64": "bigint", "float16": "real",
                           "float32": "real", "float64": "double precision"}
        self.forbidden = ["select ", "--", ";", "drop ", "where ", "from ", "delete ", "insert ", "database "]

    def config(self, filename, section):
        parser = ConfigParser()
        parser.read(filename)

        if parser.has_section(section):
            params = parser.items(section)
            for param in params:
                self.db_config[param[0]] = param[1]

        else:
            raise Exception('Section {0} not found in the {1} file'.format(section, filename))

        return self.db_config

    def connect(self):
        try:
            params = self.config(filename=self.config_path, section="psycopg2")

            print(params)

            conn_start = time.time_ns()
            print("before connection")
            self.connection = psycopg2.connect(**params)
            print("after connection")
            conn_duration = time.time_ns() - conn_start
            print(self.connection)

            cur_start = time.time_ns()
            self.cursor = self.connection.cursor()
            cur_duration = time.time_ns() - cur_start

            print('PostgresSQL database version:')
            execute_start = time.time_ns()
            self.cursor.execute('SELECT version()')
            execute_time = time.time_ns() - execute_start

            fetch_one_start = time.time_ns()
            db_version = self.cursor.fetchone()
            fetch_time = time.time_ns() - fetch_one_start

            fetch_all_start = time.time_ns()
            # db_version = self.cursor.fetchall()
            fetch_all_time = time.time_ns() - fetch_all_start

            # close_start = time.time_ns()
            # self.cursor.close()
            # close_time = time.time_ns() - close_start

            print(f"Establishing a database connection: {conn_duration / 1000000} ms.")
            print(f"Setting a cursor: {cur_duration / 1000000} ms.")
            print(f"Executing a select version statement: {execute_time / 1000000} ms.")
            print(f"Fetching a single row: {fetch_time / 1000000} ms.")
            print(f"Fetching all rows: {fetch_all_time / 1000000} ms.")
            print(f"Result: {db_version}")
            # print(f"Closing time: {close_time / 1000000} ms.")

        except psycopg2.DatabaseError as error:
            print(error.args[0])
            if "Connection refused" in error.args[0]:
                pr = os.fork()
                if pr == 0:
                    self.start_postgres()
                else:
                    os.wait()
                    self.connect()

        except Exception as exc:
            print(f"Exception, {exc}")

        finally:
            if self.connection is not None:
                print("WARNING: The connection to the database is still open!")
                # self.connection.close()
                # print('Database connection closed')

    def set_logger(self, logger):
        self.logger = logger

    def setup(self):
        try:
            connection_start = time.time_ns()
            self.connect()
            connection_time = time.time_ns() - connection_start

            print(f"Connection time: {connection_time / 1000000} ms.")

            # self.connection.close()
            # print("Database connection closed.")

        except TypeError as error:
            print(f"TypeError: {error}")

        except AttributeError as error:
            print(f"Attribute error, {error}")

    def start_postgres(self):
        os.system('sudo ../../postgres_setup/run_config.sh')

    def stop_remove_container(self):
        os.system('sudo ../../postgres_setup/stop_remove_config.sh')

    def create_schema(self, schema_name, user):
        self.cursor = self.connection.cursor()
        try:
            stmt_string = f"CREATE SCHEMA IF NOT EXISTS {schema_name} AUTHORIZATION {user}"
            sql_stmt = sql.SQL(stmt_string).format(
                schema_name=sql.Identifier(schema_name),
                user=sql.Identifier(user)
            )
            self.cursor.execute(sql_stmt)
            self.connection.commit()
        except:
            print("Schema definition problem")

    def create_table(self, table_name, schema_order):
        try:
            self.cursor = self.connection.cursor()
            self.parse_schema(schema_string=schema_order)
            create_table_query = '''
                 CREATE TABLE IF NOT EXISTS {} (
                     {}
                 );
             '''.format(table_name, schema_order)

            self.cursor.execute(create_table_query)
            self.connection.commit()

            return True

        except (Exception, psycopg2.Error, ValueError) as error:
            print("Error creating table:", error)

            # Rollback the transaction in case of an error
            if self.connection:
                self.connection.rollback()
                self.connection.commit()
            return False

    def replace_unnamed(self, df):
        df.rename(columns={'Unnamed: 0': ''})

    def insert_into_table(self, table_name, schema, data):

        try:
            self.cursor = self.connection.cursor()
            columns_string = ', '.join(data.columns)
            data_to_insert = list(data.itertuples(index=False, name=None))

            insert_query = '''
                INSERT INTO {} ({}) VALUES %s;
            '''.format(
                table_name,
                columns_string
                # Parameter placeholders
            )
            extras.execute_values(self.cursor, insert_query, data_to_insert)
            # print(sql_stmt.as_string(context=self.connection))
            # self.cursor.execute(insert_query, (row,))
            self.connection.commit()
            print(f"{len(data_to_insert)} rows inserted into '{table_name}' in schema '{schema}' successfully!")

            return True

        except (psycopg2.errors.SyntaxError, psycopg2.errors.UndefinedColumn) as error:
            self.connection.commit()
            self.logger.info(error)
            return False

    def check_table(self, table_name):
        try:
            self.cursor = self.connection.cursor()
            self.cursor.execute("SELECT * FROM " + table_name)
            data = self.cursor.fetchone()
            self.connection.commit()
            print("Table %s already exists. Row data: \n %s \n" % (table_name, data))

            return True

        except psycopg2.OperationalError:
            print("Operational Error: Table %s doesn't exist in the database.\n" % table_name)
            self.connection.commit()
            return False

        except psycopg2.errors.UndefinedTable:
            print("Undefined Table %s doesn't exist in the database.\n" % table_name)
            self.connection.commit()
            return False

    def generate_schema(self, df):
        if isinstance(df, pd.DataFrame):
            print(df.dtypes)
            schema_order = "id_X UUID DEFAULT gen_random_uuid() PRIMARY KEY, "
            df.rename(columns=lambda x: x.replace("Unnamed: ", "col_"), inplace=True)
            columns = df.columns
            for i in range(0, len(columns)):
                schema_order = schema_order + f"{columns[i]}  {self.schema_map[str(df[columns[i]].dtype)]}, "

            print(schema_order[:-2])
            return schema_order[:-2]

        else:
            print(f"The data is of format {df.type}. Cannot create schema.")

    def get_one(self, table_name):

        # sql_stmt = sql.SQL('''SELECT * FROM {table_name}''').format(
        #     table_name=sql.Identifier(table_name)
        # )

        select_query = '''
            SELECT * FROM {} LIMIT 1
        '''.format(table_name)

        self.cursor = self.connection.cursor()
        self.cursor.execute(select_query)
        data = self.cursor.fetchall()
        # print(f"Retrieved from DB:")
        # print(data)
        for row in data:
            print(f"Retrieved from DB: {row}")

        return data


    def get_data(self, table_name):

        # sql_stmt = sql.SQL('''SELECT * FROM {table_name}''').format(
        #     table_name=sql.Identifier(table_name)
        # )

        select_query = '''
            SELECT * FROM {}
        '''.format(table_name)

        self.cursor = self.connection.cursor()
        self.cursor.execute(select_query)
        data = self.cursor.fetchall()
        # print(f"Retrieved from DB:")
        # print(data)
        for row in data:
            print(f"Retrieved from DB: {row}")

        return data

    def parse_schema(self, schema_string):
        for keyword in self.forbidden:
            if keyword in schema_string.lower():
                raise ValueError(f"The provided schema contains reserved words or characters. Value: {keyword}")

    def read_file(self, file_path):
        file_extension = file_path.split('.')[-1].lower()

        blob = Path(file_path).read_bytes()

        detection = chardet.detect(blob)
        result = detection["encoding"]
        print(f"Result: {result}")

        # with open(file_path, 'rb') as f:
        #     result = chardet.detect(f.read())
        # f.close()
        supported_formats = {
            'csv': pd.read_csv,
            'xlsx': pd.read_excel,
            'xls': pd.read_excel,
            'json': pd.read_json,
            'zip': pd.read_csv,
            'gzip': pd.read_csv,
            'gz': pd.read_csv,
            'bz2': pd.read_csv,
            'zstd': pd.read_csv,
            'xz': pd.read_csv,
            'tar': pd.read_csv,
            'parquet': pd.read_parquet,
            'xml': pd.read_xml,
            'orc': pd.read_orc,
            'sas': pd.read_sas,
            'html': pd.read_html,
            'txt': pd.read_csv,
            'h5': pd.read_hdf,
            'feather': pd.read_feather
        }
        # Check if the file extension is supported
        if file_extension in supported_formats:
            # Use the corresponding read method
            read_method = supported_formats[file_extension]
            df = read_method(file_path, encoding=result, on_bad_lines='skip')
            return df
        else:
            # File extension not supported
            raise ValueError(f"Unsupported file extension: {file_extension}")


# TODO Deploy postgres via ssh connection to a dedicated IP
# TODO Execute on multiple pipelines

# TODO Instantiate validity checkers.. (e.g., config, data, file checks)
# TODO Establish databases, tables for new data
# TODO Control of DBMS resources.. Data/Table size overloads
# TODO Measure and compare the overhead of stork and PSQL to a client execution

if __name__ == '__main__':
    pp = PsqlConnector(config_path="config_db.ini")
    # pp.stop_remove_container()

    # pp.deploy_postgres()
    pp.setup()

    df = pp.read_file("../../examples/data/products.zip")
    schema_string = pp.generate_schema(df)
    # print(schema_string)

    pp.create_schema("testschema", "postgres_test_user")

    pp.create_table(table_name="testschema.testTable2", schema_order=schema_string)
    #
    # pp.insert_into_table(table_name="testSchema.testTable", schema=schema_string, data=df)
    # pp.create_table(table_name="newTable", schema_order=schema_string)
    # pp.insert_into_table(table_name="newTable", schema=schema_string, data=df)
    # pp.get_data('testSchema.testTable')
