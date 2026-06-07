#server
from flask import Flask, render_template, request, jsonify, send_from_directory, url_for, session #serverside sessions
#database
import sqlite3
# for generating session IDs
import os
import secrets #specifically using secrets as it uses OS entropy (more random than random module --> more secure)
#for password hashes
from werkzeug.security import generate_password_hash, check_password_hash
#for the dice roll api
import random

#TODO: add SESSION KEYS.... it needs the user to STAY logged in lol

app = Flask(__name__)
#checking if there is an existing secret key
if os.environ.get('SECRET_KEY'):
    app.secret_key = os.environ.get('SECRET_KEY')
else:
    #generates a 32 bit secret key 
    app.secret_key = secrets.token_urlsafe(32)
# Initialize SQLite Database
def init_db():
    conn = sqlite3.connect('dnd.db')
    cursor = conn.cursor()
    cursor.executescript('''
        CREATE TABLE IF NOT EXISTS logins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user'
        );
        CREATE TABLE IF NOT EXISTS notices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            bodytext TEXT NOT NULL,
            date INTEGER NOT NULL
        );
        CREATE TABLE IF NOT EXISTS charsheets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL REFERENCES logins(id),
            general_info TEXT NOT NULL,
            stats TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL REFERENCES logins(id),
            date DATE NOT NULL,
            notebody TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS profile (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL REFERENCES logins(id),
            display_name TEXT NOT NULL,
            bio TEXT NOT NULL
        );
    ''')
    conn.commit()
    conn.close()

# Initialize the database when the app starts
init_db()

#serving page routes
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

@app.route('/dice.html')
def dice():
    return render_template('dice.html')

@app.route('/profile.html')
def profile():
    return render_template('profile.html')

@app.route('/charsheets.html')
def charsheets():
    return render_template('charsheets.html')

@app.route('/timetable.html')
def timetable():
    return render_template('timetable.html')

@app.route('/manifest.json')
def manifest():
    return send_from_directory('static', 'manifest.json', mimetype='application/json')

#apis
@app.route('/api/login', methods=['POST'])
def verify_profile():
    try:
        data = request.json
        conn = sqlite3.connect('dnd.db')
        
        cursor = conn.cursor()
        cursor.execute('SELECT email, password FROM logins')
        #concisely creates a dict where emails map to passwords
        #e.g {dante.s@gmail.com: hashedpassword, vr.tsoi@education.nsw.gov.au: hashedpassword} etc etc
        logins = {row[0]: row[1] for row in cursor.fetchall()} 

        email = data.get('email')   
        password = data.get('password')
        if email in logins:
            hashed_pass = generate_password_hash(password)
            if logins[email] == hashed_pass:
                # email NEEDS to be passed as a one item tuple (it will be treated as a string otherwise)
                cursor.execute('SELECT id FROM logins WHERE email = ?', (email,))
                user_id = cursor.fetchone()
                # default setting: the browser cookie is non-permanent, user will log out when browser is closed
                session['user_id'] = int(user_id[0])
                print(session['user_id'])
                session.permanent = True
                cursor.close()
                return jsonify({'status': 'success'})
            else:
                cursor.close()
                return jsonify({'status': 'fail', 'message' : "Email/password is incorrect."})
        else:
            return jsonify({'status': 'fail', 'message' : "Email/password is incorrect."})
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/signup', methods=['POST'])
def save_profile():
    try:
        data = request.json
        conn = sqlite3.connect('dnd.db')
        cursor = conn.cursor()
        email = data.get('email')   
        password = data.get('password')
        hashed_pass = generate_password_hash(password)
            
        try:
            # might not be that secure lol
            if email == 'chloedndadmin@gmail.com' or 'coltondndadmin@gmail.com':
                cursor.execute('''
                    INSERT INTO logins (email, password, role)
                    VALUES (?, ?, ?)
                ''', (email, hashed_pass, 'admin'))
            else:
                cursor.execute('''
                    INSERT INTO logins (email, password, role)
                    VALUES (?, ?)
                ''', (email, hashed_pass))
            conn.commit()
            conn.close()
            return jsonify({'status': 'success'})
        except sqlite3.IntegrityError:
                return jsonify({'status': 'fail', 'message': 'Email already registered'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sessionID', methods=['GET'])
def check_sessionID():
    if 'user_id' in session:
        return jsonify({'active': True})
    else:
        return jsonify({'active': False})

@app.route('/api/dice', methods=['POST'])
def roll_dice():
    #the data this function needs is the NUMBER OF SIDES on the die
    data = request.json
    side_num = int(data.get("max-value"))
    # print(side_num)

    roll = random.randint(1, side_num)
    # print(roll)
    return jsonify({'number':roll})

@app.route('/api/savechar', methods=['POST'])
def save_char():
    try:
        if 'user_id' in session:
            data = request.json
            conn = sqlite3.connect('dnd.db')
            cursor = conn.cursor()
            general_info = data.get('general_info')   
            stats = data.get('stats')
            # try:
            cursor.execute('''
                INSERT INTO char (user_id, general_info, stats)
                VALUES (?, ?, ?)
            ''', (session['user_id'], general_info, stats))
            conn.commit()
            conn.close()
            return jsonify({'status': 'success'})
        else:
            return jsonify({'status':'fail','message':'unauthenticated'})

        # except sqlite3.IntegrityError: 
        #         return jsonify({'status': 'fail', 'message': 'Uhmmffff....'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/api/savenotes', methods=['POST'])
def save_notes():
    try:
        if 'user_id' in session:
            data = request.json
            conn = sqlite3.connect('dnd.db')
            cursor = conn.cursor()
            date = data.get('date')   
            body = data.get('body')
            # try:
            cursor.execute('''
                INSERT INTO notes (userid, date, notebody)
                VALUES (?, ?, ?)
            ''', (session['user_id'], date, body))
            conn.commit()
            conn.close()
            return jsonify({'status': 'success'})
        else:
            return jsonify({'status':'fail','message':'unauthenticated'})
        # except sqlite3.IntegrityError: 
        #         return jsonify({'status': 'fail', 'message': 'Uhmmffff....'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/getnotes', methods=['GET'])
def get_notes():
    try:
        if not 'user_id' in session:
            return jsonify({'status':'fail','message':'unauthenticated'})
        conn = sqlite3.connect('dnd.db')
        cursor = conn.cursor
        cursor.execute('SELECT date, notebody FROM notes WHERE user_id = ?', (session['user_id'],))
        notes = {row[0]: row[1] for row in cursor.fetchall()} 
        return jsonify(notes)

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/api/savenotices', methods=['GET'])
def save_notices():
    try:
        if not 'user_id' in session:
            return jsonify({'status':'fail','message':'unauthenticated'})
        conn = sqlite3.connect('dnd.db')
        cursor = conn.cursor
        cursor.execute('SELECT title, bodytext, date FROM notices', (session['user_id'],))
        notes = {row[0]: row[1] for row in cursor.fetchall()} 
        return jsonify(notes)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/getnotices', methods=['GET'])
def get_notices():
    try:
        if not 'user_id' in session:
            return jsonify({'status':'fail','message':'unauthenticated'})
        conn = sqlite3.connect('dnd.db')
        cursor = conn.cursor
        cursor.execute('SELECT title, bodytext, date FROM notices', (session['user_id'],))
        notices = []
        for row in cursor.fetchall():
            notice = {'title': row[0], 'bodytext': row[1], 'date':row[2]}
            notices.append(notice)

        return jsonify(notices)

    except Exception as e:
        return jsonify({'error': str(e)}), 500
# @app.route('/profile', methods=['GET'])
# def get_user_profile():
    
# the conext processor - runs everytime a template is rendered
    # the template can READ the variables without the view function explicitly passing them
# @app.context_processor
# def display_username():


# functions defined after this line DO NOT RUN do NOT define a function after this
if __name__ == '__main__':
    app.run(debug=True)


