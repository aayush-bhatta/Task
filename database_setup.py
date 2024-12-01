import sqlite3

def create_db():
    conn = sqlite3.connect('database/app.db')
    cursor = conn.cursor()

    # Create tables (User, Artist, Song)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS User (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            email TEXT NOT NULL
        );
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Artist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            genre TEXT
        );
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Song (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            artist_id INTEGER,
            FOREIGN KEY (artist_id) REFERENCES Artist(id)
        );
    ''')

    conn.commit()
    conn.close()

if __name__ == "__main__":
    create_db()
