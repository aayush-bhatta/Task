from flask import Flask, session, render_template, redirect, request, url_for
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Database connection
def get_db_connection():
    conn = sqlite3.connect('database/app.db')
    conn.row_factory = sqlite3.Row  # Makes rows dict-like for easier access
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

    if request.method == 'POST':  # Create artist
        name = request.form['name']
        genre = request.form['genre']
        conn.execute('INSERT INTO Artist (name, genre) VALUES (?, ?)', (name, genre))
        conn.commit()

    # Fetch artists
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


if __name__ == "__main__":
    app.run(debug=True)
