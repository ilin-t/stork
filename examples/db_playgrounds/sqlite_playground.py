import sqlite3


def main():
    data = [(1, 2.1, 1.3, 'row1 text', 7.1),
            (2, 2.2, 2.3, 'row2 text', 7.2),
            (3, 2.3, 3.3, 'row3 text', 7.3),
            (4, 2.4, 4.3, 'row4 text', 7.4),
            (5, 2.5, 5.3, 'row5 text', 7.5)]

    sqpg = SqlitePlayground()

    sqpg.connect('training.db')

    if sqpg.checkExistence("training"):

        sqpg.cur.executemany('''INSERT INTO training VALUES (?, ?, ?, ?, ?)''', data)

        for row in sqpg.cur.execute('SELECT * FROM training'):
            print(row)

    else:
        sqpg.cur.execute('''CREATE TABLE training (id int primary key, col1 real, col2 real, col3 text, col4 real)''')

        print("Created table training \n")

        sqpg.cur.executemany('''INSERT INTO training VALUES (?, ?, ?, ?, ?)''', data)

        for row in sqpg.cur.execute('SELECT * FROM training'):
            print(row)

    sqpg.con.commit()
    sqpg.con.close()


class SqlitePlayground:

    def __init__(self):
        self.con = None
        self.cur = None

    def connect(self, db):
        self.con = sqlite3.connect(db)
        self.cur = self.con.cursor()

    def closeConnection(self):
        self.con.close()

    def createTable(self, name, schema):
        self.cur.execute("CREATE TABLE " + name + " VALUES " + schema)
        self.con.commit()

    def checkExistence(self, table):

        try:
            self.cur.execute("SELECT * FROM " + table)
            data = self.cur.fetchone()
            print("Table %s already exists. Row data: \n %s \n" % (table, data))

            return True

        except sqlite3.OperationalError:
            print("Table %s doesn't exist in the database.\n" % table)
            return False


if __name__ == '__main__':
    main()
