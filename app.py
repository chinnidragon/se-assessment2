from flask import Flask, render_template, request, jsonify, send_from_directory, url_for
import sqlite3

app = Flask(__name__)

# Initialize SQLite Database
def init_db():
    conn = sqlite3.connect('dnd.db')
    cursor = conn.cursor()
    cursor.executescript('''
        CREATE TABLE IF NOT EXISTS logins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS notices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titletext TEXT NOT NULL,
            bodytext TEXT NOT NULL,
            date INTEGER NOT NULL
        );
        CREATE TABLE IF NOT EXISTS charsheets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            info TEXT NOT NULL
        );
    ''')
    conn.commit()
    conn.close()

# Initialize the database when the app starts
init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login.html')
def login():
    return render_template('login.html')

@app.route('/signup.html')
def signup():
    return render_template('signup.html')


@app.route('/homepage.html')
def homepage():
    return render_template('homepage.html')

@app.route('/manifest.json')
def manifest():
    return send_from_directory('static', 'manifest.json', mimetype='application/json')

@app.route('/dnd.db', methods=['GET'])
def get_profile():
    try:
        conn = sqlite3.connect('dnd.db')
        cursor = conn.cursor()
        cursor.execute('SELECT email FROM logins')
        username = {row[0]: row[1] for row in cursor.fetchall()} 
        return jsonify(username)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/save_login', methods=['POST'])
def save_login():
    try:
        data = request.json
        conn = sqlite3.connect('dnd.db')
        cursor = conn.cursor()
        for email, password in data.items():
            cursor.execute('''
                INSERT INTO logins (email, password)
                VALUES (?, ?)
            ''', (email, password))
        conn.commit()
        conn.close()
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)


# @app.route('/')
# def index():
#     return 'index'

# @app.route('/login')
# def login():
#     return 'login'

# @app.route('/user/<username>')
# def profile(username):
#     return f'{username}\'s profile'

# with app.test_request_context():
#     print(url_for('index'))
#     print(url_for('login'))
#     print(url_for('login', next='/'))
#     print(url_for('profile', username='John Doe'))