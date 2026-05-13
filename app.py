from flask import Flask, render_template, request, jsonify, send_from_directory
import sqlite3

app = Flask(__name__)

# Initialize SQLite Database
def init_db():
    conn = sqlite3.connect('dnd.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS 
        login (
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL UNIQUE,
            # note TEXT NOT NULL
        )
        CREATE TABLE IF NOT EXISTS 
        notices (
            titletext TEXT NOT NULL,
            bodytext TEXT NOT NULL,
            date INTEGER NOT NULL
        )
        CREATE TABLE IF NOT EXISTS 
        charsheets (
            name TEXT NOT NULL,
            info TEXT NOT NULL,
            # img INTEGER NOT NULL ts needs to be a URL... to the png of the character...
        )
    ''')
    conn.commit()
    conn.close()

# Initialize the database when the app starts
init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/manifest.json')
def manifest():
    return send_from_directory('static', 'manifest.json', mimetype='application/json')

@app.route('/get-login', methods=['GET'])
def get_login():
    try:
        conn = sqlite3.connect('memberlogin.db')
        cursor = conn.cursor()
        cursor.execute('SELECT day, note FROM notes')
        notes = {row[0]: row[1] for row in cursor.fetchall()}
        conn.close()
        return jsonify(notes)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/save_login', methods=['POST'])
def save_notes():
    try:
        data = request.json
        conn = sqlite3.connect('memberlogin.db')
        cursor = conn.cursor()
        for day, note in data.items():
            cursor.execute('''
                INSERT INTO notes (day, note)
                VALUES (?, ?)
                ON CONFLICT(day) DO UPDATE SET note=excluded.note
            ''', (day, note))
        conn.commit()
        conn.close()
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)