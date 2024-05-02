import os
from pathlib import Path

import cchardet as chardet
from sqlalchemy import create_engine, text, MetaData, inspect
from sqlalchemy.exc import SQLAlchemyError

import time

import pandas as pd


class sqliteConnector:
    def __init__(self, db_file):
        self.db_config = {}
        self.engine = create_engine('sqlite:///' + db_file)
        self.logger = None
        self.connection = self.engine.connect()
        self.schema_map = {"object": "varchar", "int64": "bigint", "int8": "smallint", "int16": "smallint",
                           "int32": "integer", "uint8": "smallint",
                           "uint16": "smallint", "uint32": "integer", "uint64": "bigint", "float16": "real",
                           "float32": "real", "float64": "double precision"}
        self.forbidden = ["select ", "--", ";", "drop ", "where ", "from ", "delete ", "insert ", "database "]

    def connect(self):
        try:

            conn_start = time.time_ns()
            print("before connection")
            self.connection = self.engine.connect()
            print("after connection")
            conn_duration = time.time_ns() - conn_start
            print(self.connection)

            fetch_all_start = time.time_ns()
            fetch_all_time = time.time_ns() - fetch_all_start

            print(f"Establishing a database connection: {conn_duration / 1000000} ms.")
            print(f"Fetching all rows: {fetch_all_time / 1000000} ms.")
            # print(f"Closing time: {close_time / 1000000} ms.")

        except SQLAlchemyError as error:
            print(error.args[0])
            if "Connection refused" in error.args[0]:
                pr = os.fork()
                if pr == 0:
                    return False
                else:
                    os.wait()
                    self.connect()

        except Exception as exc:
            print(f"Exception, {exc}")

        finally:
            if self.connection is not None:
                print("WARNING: The connection to the database is still open!")

    def set_logger(self, logger):
        self.logger = logger

    def setup(self):
        try:
            connection_start = time.time_ns()
            self.connect()
            connection_time = time.time_ns() - connection_start

            print(f"Connection time: {connection_time / 1000000} ms.")

        except TypeError as error:
            print(f"TypeError: {error}")

        except AttributeError as error:
            print(f"Attribute error, {error}")

    def create_table(self, table_name, schema_order):
        try:
            self.parse_schema(schema_string=schema_order)
            create_table_query = '''
                 CREATE TABLE IF NOT EXISTS {} (
                     {}
                 );
             '''.format(table_name, schema_order)

            self.connection.execute(create_table_query)

            return True

        except (Exception, SQLAlchemyError, ValueError) as error:
            print("Error creating table:", error)

    def replace_unnamed(self, df):
        df.rename(columns={'Unnamed: 0': ''})



    def generate_schema(self, df):
        if isinstance(df, pd.DataFrame):
            print(df.dtypes)
            schema_order = "id_X INTEGER PRIMARY KEY AUTOINCREMENT, "
            df.rename(columns=lambda x: x.replace("Unnamed: ", "col_"), inplace=True)
            columns = df.columns
            for i in range(0, len(columns)):
                schema_order = schema_order + f"{columns[i]}  {self.schema_map[str(df[columns[i]].dtype)]}, "

            print(schema_order[:-2])
            return schema_order[:-2]

        else:
            print(f"The data is of format {df.type}. Cannot create schema.")

    def get_one(self, table_name):

        select_query = '''
            SELECT * FROM {} LIMIT 1
        '''.format(table_name)

        data = self.connection.execute(text(select_query))
        for row in data:
            print(f"Retrieved from DB: {row}")

        return data

    def get_data(self, table_name):

        select_query = '''
            SELECT * FROM {}
        '''.format(table_name)

        data = self.connection.execute(text(select_query))
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
            'feather': pd.read_feather,
        }
        # Check if the file extension is supported
        if file_extension in supported_formats:
            read_method = supported_formats[file_extension]
            df = read_method(file_path, encoding=result, on_bad_lines='skip')
            return df
        else:
            # File extension not supported
            raise ValueError(f"Unsupported file extension: {file_extension}")

    def get_schema(self, table):
        metadata = MetaData()
        inspector = inspect(self.engine)
        columns = inspector.get_columns(table)

        # Print the schema
        for column in columns:
            print(f"Column Name: {column['name']}, Type: {column['type']}")
