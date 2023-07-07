import psycopg2
from configparser import ConfigParser


class PostgresqlPlayground():
    def __init__(self):
        self.db = {}

    def config(self, filename='database.ini', section='postgresql'):
        parser = ConfigParser()
        parser.read(filename)

        if parser.has_section(section):
            params = parser.items(section)
            for param in params:
                self.db[param[0]] = param[1]

        else:
            raise Exception('Section {0} not found in the {1} file'.format(section, filename))

        return self.db

    def connect(self):
        conn = None

        try:
            params = self.config()

            conn = psycopg2.connect(**params)
            cur = conn.cursor()

            print('PostgreSQL database version:')
            cur.execute('SELECT version()')

            # display the PostgreSQL database server version
            db_version = cur.fetchone()
            print(db_version)

            # close the communication with the PostgreSQL
            cur.close()

        except (Exception, psycopg2.DatabaseError) as error:
            print(error)

        finally:
            if conn is not None:
                conn.close()
                print('Database connection closed.')
#
#
if __name__ == '__main__':
    pp = PostgresqlPlayground()
    pp.connect()

# conn = psycopg2.connect("dbname=suppliers user=postgres")
#
# conn = psycopg2.connect(
#     database="suppliers",
#     user="postgres")
#
# cur = conn.cursor()
# # cur.execute("SELECT * FROM film")
# # cur.
