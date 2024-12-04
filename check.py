import sqlite3

def check_schema():
    connection = sqlite3.connect('database/app.db')
    cursor = connection.cursor()

    cursor.execute('PRAGMA table_info(User);')
    columns = cursor.fetchall()
    for column in columns:
        print(column)

check_schema()
