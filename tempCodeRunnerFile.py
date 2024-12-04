from flask import Flask, session, render_template, redirect, request, url_for
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database connection
def get_db_connection():
    conn = sqlite3.connect('database/app.db', check_same_thread=False)
    conn.execute('PRAGMA journal_mode=WAL;')  # Enable WAL mode for better concurrency
    return conn


# Home route
@app.route('/')
def home():
    if 'user_id' in session:
        return redirect('/dashboard')
    return redirect('/login')

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        conn = get_db_connection()
        user = conn.execute('SELECT * FROM User WHERE username = ? AND password = ?', (username, password)).fetchone()
        conn.close()
        if user:
            session['user_id'] = user['id']
            return redirect('/dashboard')
        else:
            return "Invalid credentials"
    return render_template('login.html')

# Register route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        conn = get_db_connection()
        try:
            conn.execute('INSERT INTO User (username, password, email) VALUES (?, ?, ?)', (username, password, email))
            conn.commit()
        except sqlite3.IntegrityError:
            return "Username or Email already exists"
        conn.close()
        return redirect('/login')
    return render_template('register.html')

# Dashboard route
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')
    return render_template('dashboard.html')

# Logout route
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect('/login')


@app.route('/users', methods=['GET', 'POST'])
def users():
    if 'user_id' not in session:
        return redirect('/login')

    conn = get_db_connection()

    if request.method == 'POST':  # Create user
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        conn.execute('INSERT INTO User (username, password, email) VALUES (?, ?, ?)', (username, password, email))
        conn.commit()

    # Fetch users
    users = conn.execute('SELECT * FROM User').fetchall()
    conn.close()
    return render_template('users.html', users=users)

@app.route('/artists', methods=['GET', 'POST'])

def artists():
    if 'user_id' not in session:
        return redirect('/login')

    conn = get_db_connection()

    if request.method == 'POST':  # Add new artist
        name = request.form['name']
        dob = request.form['dob']
        gender = request.form['gender']
        address = request.form['address']
        first_release_year = request.form['first_release_year']
        no_of_albums_released = request.form['no_of_albums_released']

        conn.execute('''
            INSERT INTO Artist (name, dob, gender, address, first_release_year, no_of_albums_released)
            VALUES (?, ?, ?, ?, ?, ?)''',
            (name, dob, gender, address, first_release_year, no_of_albums_released))
        conn.commit()

    # Fetch all artists
    artists = conn.execute('SELECT * FROM Artist').fetchall()
    conn.close()
    return render_template('artists.html', artists=artists)

def list_artists():
    conn = None
    artists = []
    try:
        conn = get_db_connection()
        artists = conn.execute('SELECT * FROM Artist').fetchall()  # Fetch all artists
    except sqlite3.OperationalError as e:
        print(f"Database error: {e}")
    finally:
        if conn:
            conn.close()

    return render_template('artists.html', artists=artists)

def show_artists():
    conn = get_db_connection()
    artists = conn.execute('SELECT * FROM Artist').fetchall()
    conn.close()
    return render_template('artists.html', artists=artists)



@app.route('/artists/<int:artist_id>/songs', methods=['GET', 'POST'])
def songs(artist_id):
    if 'user_id' not in session:
        return redirect('/login')

    conn = get_db_connection()

    if request.method == 'POST':  # Add a song
        title = request.form['title']
        conn.execute('INSERT INTO Song (title, artist_id) VALUES (?, ?)', (title, artist_id))
        conn.commit()

    # Fetch songs for the artist
    songs = conn.execute('SELECT * FROM Song WHERE artist_id = ?', (artist_id,)).fetchall()
    artist = conn.execute('SELECT * FROM Artist WHERE id = ?', (artist_id,)).fetchone()
    conn.close()

    return render_template('songs.html', songs=songs, artist=artist)

# Add user route
@app.route('/users/add', methods=['GET', 'POST'])
def add_user():
    if 'user_id' not in session:
        return redirect('/login')

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        phone = request.form['phone']
        dob = request.form['dob']
        gender = request.form['gender']
        address = request.form['address']

        conn = get_db_connection()
        conn.execute('INSERT INTO User (username, password, email, phone, dob, gender, address) VALUES (?, ?, ?, ?, ?, ?, ?)',
                     (username, password, email, phone, dob, gender, address))
        conn.commit()
        conn.close()
        return redirect('/users')

    return render_template('add_user.html')

# Edit user route
@app.route('/users/edit/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    if 'user_id' not in session:
        return redirect('/login')

    conn = get_db_connection()
    user = conn.execute('SELECT * FROM User WHERE id = ?', (user_id,)).fetchone()

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        phone = request.form['phone']
        dob = request.form['dob']
        gender = request.form['gender']
        address = request.form['address']

        conn.execute('UPDATE User SET username = ?, email = ?, phone = ?, dob = ?, gender = ?, address = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
                     (username, email, phone, dob, gender, address, user_id))
        conn.commit()
        conn.close()
        return redirect('/users')

    conn.close()
    return render_template('edit_user.html', user=user)

# Delete user route
@app.route('/users/delete/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    if 'user_id' not in session:
        return redirect('/login')

    conn = get_db_connection()
    conn.execute('DELETE FROM User WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()

    return {"message": "User deleted successfully"}


@app.route('/update_user', methods=['POST'])
def update_user():
    user_id = request.form.get('id')
    name = request.form.get('name')
    email = request.form.get('email')
    # role = request.form.get('role')

    # Update the user in the database
    conn = get_db_connection()
    conn.execute('UPDATE User SET username = ?, email = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
                 (name, email, user_id))
    conn.commit()
    conn.close()

    return redirect(url_for('users'))  # Redirect to the user list page


# @app.route('/artists/add', methods=['GET', 'POST'])
# def add_artist():
#     if 'user_id' not in session:
#         return redirect('/login')

#     if request.method == 'POST':
#         name = request.form['name']
#         dob = request.form['dob']
#         gender = request.form['gender']
#         address = request.form['address']
#         first_release_year = request.form['first_release_year']
#         no_of_albums_released = request.form['no_of_albums_released']

#         conn = get_db_connection()
#         conn.execute('INSERT INTO Artist (name, dob, gender, address, first_release_year, no_of_albums_released) VALUES (?, ?, ?, ?, ?, ?)',
#                      (name, dob, gender, address, first_release_year, no_of_albums_released))
#         conn.commit()
#         conn.close()
#         return redirect('/artists')

#     return render_template('add_artist.html')


# Edit Artist Route
# @app.route('/artists/edit/<int:artist_id>', methods=['GET', 'POST'])
# def edit_artist(artist_id):
#     if 'user_id' not in session:
#         return redirect('/login')

#     conn = get_db_connection()
#     artist = conn.execute('SELECT * FROM Artist WHERE id = ?', (artist_id,)).fetchone()

#     if request.method == 'POST':
#         name = request.form['name']
#         dob = request.form['dob']
#         gender = request.form['gender']
#         address = request.form['address']
#         first_release_year = request.form['first_release_year']
#         no_of_albums_released = request.form['no_of_albums_released']

#         conn.execute('UPDATE Artist SET name = ?, dob = ?, gender = ?, address = ?, first_release_year = ?, no_of_albums_released = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?',
#                      (name, dob, gender, address, first_release_year, no_of_albums_released, artist_id))
#         conn.commit()
#         conn.close()
#         return redirect('/artists')

#     conn.close()
#     return render_template('edit_artist.html', artist=artist)


# Delete Artist Route
# @app.route('/artists/delete/<int:artist_id>', methods=['DELETE'])
# def delete_artist(artist_id):
#     if 'user_id' not in session:
#         return redirect('/login')

#     conn = get_db_connection()
#     conn.execute('DELETE FROM Artist WHERE id = ?', (artist_id,))
#     conn.commit()
#     conn.close()

#     return {"message": "Artist deleted successfully"}



@app.route('/artists/add', methods=['GET', 'POST'])
def add_artist():
    if 'user_id' not in session:
        return redirect('/login')

    if request.method == 'POST':
        name = request.form['name']
        dob = request.form['dob']
        gender = request.form['gender']
        address = request.form['address']
        first_release_year = request.form['first_release_year']
        no_of_albums_released = request.form['no_of_albums_released']

        conn = None
        try:
            conn = get_db_connection()
            conn.execute('''
                INSERT INTO Artist (name, dob, gender, address, first_release_year, no_of_albums_released)
                VALUES (?, ?, ?, ?, ?, ?)''',
                (name, dob, gender, address, first_release_year, no_of_albums_released))
            conn.commit()
        except Exception as e:
            print(f"Error: {e}")
        finally:
            if conn:
                conn.close()

        return redirect('/artists')

    return render_template('add_artist.html')


@app.route('/artists/edit/<int:artist_id>', methods=['GET', 'POST'])
def edit_artist(artist_id):
    if 'user_id' not in session:
        return redirect('/login')

    conn = get_db_connection()
    artist = conn.execute('SELECT * FROM Artist WHERE id = ?', (artist_id,)).fetchone()

    if request.method == 'POST':
        name = request.form['name']
        dob = request.form['dob']
        gender = request.form['gender']
        address = request.form['address']
        first_release_year = request.form['first_release_year']
        no_of_albums_released = request.form['no_of_albums_released']

        conn.execute('''
            UPDATE Artist
            SET name = ?, dob = ?, gender = ?, address = ?, first_release_year = ?, no_of_albums_released = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?''',
            (name, dob, gender, address, first_release_year, no_of_albums_released, artist_id))
        conn.commit()
        conn.close()

        return redirect('/artists')

    conn.close()
    return render_template('edit_artist.html', artist=artist)


@app.route('/artists/delete/<int:artist_id>', methods=['DELETE'])
def delete_artist(artist_id):
    if 'user_id' not in session:
        return redirect('/login')

    conn = get_db_connection()
    conn.execute('DELETE FROM Artist WHERE id = ?', (artist_id,))
    conn.commit()
    conn.close()

    return {"message": "Artist deleted successfully"}


@app.route('/artists/<int:artist_id>/songs', methods=['GET', 'POST'])
def manage_songs(artist_id):
    if 'user_id' not in session:
        return redirect('/login')

    conn = get_db_connection()

    if request.method == 'POST':  # Add song
        title = request.form['title']
        album_name = request.form['album_name']
        genre = request.form['genre']

        conn.execute('''
            INSERT INTO Song (title, album_name, genre, artist_id)
            VALUES (?, ?, ?, ?)''',
            (title, album_name, genre, artist_id))
        conn.commit()

    # Fetch songs for the artist
    songs = conn.execute('SELECT * FROM Song WHERE artist_id = ?', (artist_id,)).fetchall()
    artist = conn.execute('SELECT * FROM Artist WHERE id = ?', (artist_id,)).fetchone()
    conn.close()

    return render_template('songs.html', artist=artist, songs=songs)


if __name__ == "__main__":
    app.run(debug=True)
