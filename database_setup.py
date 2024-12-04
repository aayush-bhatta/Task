import sqlite3

# Define the database schema
def setup_database():
    connection = sqlite3.connect('database/app.db')
    cursor = connection.cursor()

    # Drop the User table if it exists (so we can recreate it)
    cursor.execute('DROP TABLE IF EXISTS User')

    # Create User table with the 'username' column
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS User (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL,
        email TEXT,
        phone TEXT,
        dob TEXT,
        gender TEXT,
        address TEXT,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Create Artist table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Artist (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        dob TEXT,
        gender TEXT,
        address TEXT,
        first_release_year INTEGER,
        no_of_albums_released INTEGER,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # Create Song table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Song (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        album_name TEXT,
        genre TEXT,
        artist_id INTEGER NOT NULL,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (artist_id) REFERENCES Artist(id)
    )
    ''')

    connection.commit()
    connection.close()

# Execute the setup
if __name__ == '__main__':
    setup_database()
    print("Database setup complete.")

# Function to check the schema and print the table structure
def check_schema():
    connection = sqlite3.connect('database/app.db')
    cursor = connection.cursor()

    # Get table information for the 'User' table
    cursor.execute('PRAGMA table_info(User);')
    columns = cursor.fetchall()
    for column in columns:
        print(column)

check_schema()
