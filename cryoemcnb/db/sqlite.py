import os
from sqlite3 import dbapi2 as sqlite
from cryoemcnb.constants import DBNAME


def connect_to_ddbb():
    connection = sqlite.connect(database=os.path.join(os.path.dirname(os.path.abspath(__file__)), DBNAME))
    create_ddbb_data(connection)
    return connection


def create_ddbb_data(connection):
    cursor = connection.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS project_info (
                        project_name TEXT NOT NULL,
                        key TEXT NOT NULL,
                        value TEXT NOT NULL);''')
    connection.commit()


def close_connection_to_ddbb(connection):
    connection.close()
