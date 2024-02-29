import os
import re

import psycopg2
from configparser import ConfigParser
import time

import pandas as pd

from psycopg2 import sql


class PsqlConnector:
    def __init__(self):
        self.db_config = {}
        self.connection = None
        self.cursor = None
        self.schema_map = {"object": "varchar", "int64": "bigint", "int8": "smallint", "int16": "smallint",
                           "int32": "integer", "uint8": "smallint",
                           "uint16": "smallint", "uint32": "integer", "uint64": "bigint", "float16": "real",
                           "float32": "real", "float64": "double precision"}
        self.forbidden = ["select ", "--", ";", "drop ", "where ", "from ", "delete ", "insert ", "database "]

    def config(self, filename='config_db.ini', section='psycopg2'):
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
            params = self.config()

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
        self.cursor = self.connection.cursor()

        try:
            self.parse_schema(schema_string=schema_order)
        except ValueError as err:
            print(err)
            return False

        # SQL statement to create a table with the specified schema
        create_table_query = f'''
            CREATE TABLE IF NOT EXISTS {table_name} (
                {schema_order}
            );
        '''


        self.cursor.execute(create_table_query)
        self.connection.commit()



    def insert_into_table(self, table_name, schema, data):
        # if not self.check_table(table_name):
        #     self.create_table(table_name=table_name, schema_order=schema)

        self.cursor = self.connection.cursor()
        for row in list(data.itertuples(index=False, name=None)):
            print(row)
            # sql_stmt = sql.SQL("""INSERT INTO {table_name} VALUES {row}""").format(
            #     table_name=sql.Identifier(table_name),
            #     row=sql.Literal(wrapped=row)
            # )
            print(schema)

            insert_query = '''
                INSERT INTO {}
                VALUES %s;
            '''.format(
                table_name  # Parameter placeholders
            )

            # print(sql_stmt.as_string(context=self.connection))
            self.cursor.execute(insert_query, (row,))
        self.connection.commit()

    def check_table(self, table_name):
        try:
            self.cursor = self.connection.cursor()
            self.cursor.execute("SELECT * FROM " + table_name)
            data = self.cursor.fetchone()
            print("Table %s already exists. Row data: \n %s \n" % (table_name, data))

            return True

        except psycopg2.OperationalError:
            print("Table %s doesn't exist in the database.\n" % table_name)
            return False

        except psycopg2.errors.UndefinedTable:
            print("Table %s doesn't exist in the database.\n" % table_name)
            return False

    def generate_schema(self, df):

        print(df.dtypes)
        schema_order = ""
        columns = df.columns
        for i in range(0, len(columns)):
            column_stripped = columns[i].replace("Unnamed: ", "col_")
            if i==0:
                schema_order = schema_order + f"{column_stripped}  {self.schema_map[str(df[columns[i]].dtype)]} PRIMARY KEY, "
            else:
                schema_order = schema_order + f"{column_stripped} {self.schema_map[str(df[columns[i]].dtype)]}, "

        print(schema_order)

        return schema_order[:-2]

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


# TODO Deploy postgres via ssh connection to a dedicated IP
# TODO Execute on multiple pipelines

# TODO Instantiate validity checkers.. (e.g., config, data, file checks)
# TODO Establish databases, tables for new data
# TODO Control of DBMS resources.. Data/Table size overloads
# TODO Measure and compare the overhead of stork and PSQL to a client execution

if __name__ == '__main__':
    pp = PsqlConnector()
    # pp.stop_remove_container()

    # pp.deploy_postgres()
    pp.setup()

    df = pd.read_csv("../../examples/data/products.csv")
    schema_string = pp.generate_schema(df)
    print(schema_string)

    pp.create_schema("testSchema", "postgres_test_user")
    print(pp.check_table(table_name="testSchema.testTable"))

    pp.create_table(table_name="testSchema.testTable", schema_order=schema_string)
    #
    # pp.insert_into_table(table_name="testSchema.testTable", schema=schema_string, data=df)
    # pp.create_table(table_name="newTable", schema_order=schema_string)
    # pp.insert_into_table(table_name="newTable", schema=schema_string, data=df)
    pp.get_data('testSchema.testTable')
