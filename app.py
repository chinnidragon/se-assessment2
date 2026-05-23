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
            user_id INTEGER NOT NULL REFERENCES logins(id)
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

# @app.route('/', methods=['GET'])
# def get_profile():
#     try:
#         conn = sqlite3.connect('dnd.db')
#         cursor = conn.cursor()
#         cursor.execute('SELECT email FROM logins')
#         username = {row[0]: row[1] for row in cursor.fetchall()} 
#         return jsonify(username)
#     except Exception as e:
#         return jsonify({'error': str(e)}), 500

@app.route('/api/login', methods=['POST'])
def verify_profile():
    try:
        data = request.json
        conn = sqlite3.connect('dnd.db')
        
        cursor = conn.cursor()
        cursor.execute('SELECT email, password FROM logins')
        logins = {row[0]: row[1] for row in cursor.fetchall()} 
        
        email = data.get('email')   
        password = data.get('password')
        if email in logins:
            if password == logins[email]:
                return True
            else:
                return False
        else:
            return False
            

        
        # if data.items() in logins:
        #     return jsonify({'status': 'success'})
        # else:
        #     return jsonify({'status': 'fail'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500



@app.route('/api/signup', methods=['POST'])
def save_profile():
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