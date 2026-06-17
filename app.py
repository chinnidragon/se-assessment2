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

#debug
# app.secret_key = 676767676767

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
            user_id INTEGER NOT NULL REFERENCES logins(id),
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
            notes TEXT NOT NULL
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

@app.route('/auth/login')
def login():
    return render_template('login.html')

@app.route('/auth/signup')
def signup():
    return render_template('signup.html')

@app.route('/home')
def home():
    return render_template('homepage.html')

@app.route('/diceroll')
def dice():
    return render_template('dice.html')

@app.route('/profile')
def profile():
    return render_template('profile.html')

@app.route('/charactersheets')
def charsheets():
    return render_template('charsheets.html')

@app.route('/timetable')
def timetable():
    return render_template('timetable.html')

@app.route('/notes')
def notes():
    return render_template('notes.html')

@app.route('/logout')
def logout():
    return render_template('logout.html')

@app.route('/notices')
def notices():
    return render_template('notices.html')

@app.route('/notices/create')
def create_notices():
    return render_template('create_notice.html')

@app.route('/manifest.json')
def manifest():
    return send_from_directory('static', 'manifest.json', mimetype='application/json')

@app.route('/username')
def user():
    return session.get('username')
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
        # more concise than 2 if statements
        if email in logins and check_password_hash(logins[email], password):
            # email NEEDS to be passed as a one item tuple (it will be treated as a string otherwise)
            cursor.execute('SELECT id FROM logins WHERE email = ?', (email,))
            user_id = cursor.fetchone()

            session['user_id'] = int(user_id[0])
            cursor.execute('SELECT display_name FROM profile WHERE user_id = ?', (session['user_id'],))
            username = cursor.fetchone()
            session['username'] = username
            # default setting: the browser cookie is non-permanent, user will log out when browser is closed
            session.permanent = True
            cursor.close()
            conn.close()
            return jsonify({'status': 'success'})
        else:
            cursor.close()
            conn.close()
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
            if email in ('chloedndadmin@gmail.com', 'coltondndadmin@gmail.com'):
                cursor.execute('''
                    INSERT INTO logins (email, password, role)
                    VALUES (?, ?, ?)
                ''', (email, hashed_pass, 'admin'))
            else:
                cursor.execute('''
                    INSERT INTO logins (email, password, role)
                    VALUES (?, ?, ?)
                ''', (email, hashed_pass, 'user'))
            
            cursor.execute('SELECT id FROM logins WHERE email = ?', (email,))
            user_id = cursor.fetchone()
            session['user_id'] = int(user_id[0])
            cursor.execute('SELECT display_name FROM profile WHERE user_id = ?', (session['user_id'],))
            username = cursor.fetchone()
            session['username'] = username
            # default setting: the browser cookie is non-permanent, user will log out when browser is closed
            session.permanent = True
            conn.commit()
            conn.close()

            return jsonify({'status': 'success'})
        except sqlite3.IntegrityError:
                return jsonify({'status': 'fail', 'message': 'Email already registered'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/logout', methods=['GET'])
def user_logout():
    try:
        session.pop('user_id', None) 
        return jsonify({'status':'success'})
    except Exception as e:
        return jsonify({'status':'fail'})

@app.route('/api/sessionID', methods=['GET'])
def check_sessionID():
    if 'user_id' in session:
        return jsonify({'active': True})
    else:
        return jsonify({'active': False})
    
@app.route('/api/adminnotices', methods=['GET'])
def admin_createnotice():
    if 'user_id' in session:
        conn = sqlite3.connect('dnd.db')
        cursor = conn.cursor()
        cursor.execute('SELECT id FROM logins WHERE role = admin')
        adminIDs = cursor.fetchall()
        if session.get('user_id') in adminIDs:
            return jsonify({'admin': True})
        else:
            return jsonify({'admin': False})
    else:
        return jsonify({'admin': False})



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
            print(date)
            body = data.get('body')
            print(body)
            cursor.execute('''
                INSERT INTO notes (user_id, date, notes)
                VALUES (?, ?, ?)
            ''', (session.get('user_id'), date, body))
            conn.commit()
            conn.close()
            return jsonify({'status': 'success'})
        else:
            return jsonify({'status':'fail','message':'unauthenticated'})
        # except sqlite3.IntegrityError: 
        #         return jsonify({'status': 'fail', 'message': 'Uhmmffff....'})
    except Exception as e:
        return jsonify({'status': 'fail', 'message': str(e)}), 500

@app.route('/api/getnotes', methods=['GET'])
def get_notes():
    try:
        if 'user_id' in session:
            conn = sqlite3.connect('dnd.db')
            cursor = conn.cursor()
            cursor.execute('SELECT date, notes FROM notes WHERE user_id = ? ORDER BY date desc', (session['user_id'],))
            print(cursor.fetchall())
            rows = cursor.fetchall();
            notices = [
                {'date': r[2], 'notes': r[3]}
                for r in rows
            ]
            conn.close()
            # notes = {}
            # notes = {row[0]: row[1] for row in cursor.fetchall()}
            # for row in cursor.fetchall():
            #     row_note = {}
            #     date = row[0]
            #     note = row[1]
            #     row_note['date'] = date
            #     row_note['note']= note
            #     notes
            # print(notes)
            return jsonify({'status': 'success', 'notes': notes})
        else:
            return jsonify({'status':'fail','message':'unauthenticated'})
    except Exception as e:
        return jsonify({'status': 'fail', 'message': str(e)}), 500
    

#notices basically the EXACT same logic as the notes
@app.route('/api/savenotices', methods=['POST'])
def save_notices():
    try:
        if 'user_id' in session:
            data = request.json
            conn = sqlite3.connect('dnd.db')
            cursor = conn.cursor()
            date = data.get('date') 
            title = data.get('title')
            body = data.get('body')
            cursor.execute('''
                INSERT INTO notices (user_id, title, bodytext, date)
                VALUES (?, ?, ?, ?)
            ''', (session['user_id'], title, body, date))
            conn.commit()
            conn.close()
            return jsonify({'status': 'success'})
        else:
            return jsonify({'status':'fail','message':'unauthenticated'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/getnotices', methods=['GET'])
def get_notices():
    try:
        if not 'user_id' in session:
            return jsonify({'status':'fail','message':'unauthenticated'})
        conn = sqlite3.connect('dnd.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT 
                notices.title, 
                notices.bodytext, 
                notices.date, 
                logins.email
            FROM notices 
            JOIN logins ON notices.id = logins.user_id''')
        notices = []
        for row in cursor.fetchall():
            notice = {'title': row[0], 'bodytext': row[1], 'date':row[2]}
            notices.append(notice)
        return jsonify({"status": "success", "notices": jsonify(notices)})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

# functions defined after this line DO NOT RUN do NOT define a function after this
if __name__ == '__main__':
    app.run(debug=True)