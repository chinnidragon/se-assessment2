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
#for database
import json


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
            user_id INTEGER NOT NULL REFERENCES logins(id),
            title TEXT NOT NULL,
            body TEXT NOT NULL,
            date TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS charsheets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL REFERENCES logins(id),
            name TEXT NOT NULL,
            info TEXT NOT NULL,
            stats TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS event (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL REFERENCES logins(id),
            date TEXT NOT NULL,
            title TEXT NOT NULL,
            body TEXT
        );
        CREATE TABLE IF NOT EXISTS notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL REFERENCES logins(id),
            date TEXT NOT NULL,
            notes TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS profile (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL REFERENCES logins(id),
            display_name TEXT NOT NULL,
            bio TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS timetable (
            active_days JSON
        );
    ''')
    conn.commit()
    conn.close()

# initialise the database when the app starts
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

@app.route('/profile/edit')
def editprofile():
    return render_template('edit_profile.html')

@app.route('/charactersheets')
def charsheets():
    return render_template('charsheets.html')

@app.route('/charactersheets/view')
def view_chars():
    return render_template('view_chars.html')

@app.route('/timetable')
def timetable():
    return render_template('timetable.html')

@app.route('/timetable/create')
def t_event():
    return render_template('create_event.html')

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
    return render_template('create_notices.html')

@app.route('/manifest.json')
def manifest():
    return send_from_directory('static', 'manifest.json', mimetype='application/json')

# @app.route('/stylesheet.css')
# def manifest():
#     return send_from_directory('static', 'manifest.json', mimetype='stylesheet/css')

@app.route('/slices')
def slices():
    return send_from_directory('static/images', 'millionsslices.png', mimetype='image/png')

@app.route('/20d')
def twenty_d():
    return send_from_directory('static/images', 'millionsslices.png', mimetype='image/png')

@app.route('/12d')
def twelve_d():
    return send_from_directory('static/images', 'millionsslices.png', mimetype='image/png')

@app.route('/10d')
def ten_d():
    return send_from_directory('static/images', 'millionsslices.png', mimetype='image/png')

@app.route('/6d')
def six_d():
    return send_from_directory('static/images', 'millionsslices.png', mimetype='image/png')

@app.route('/4d')
def four_d():
    return send_from_directory('static/images', 'millionsslices.png', mimetype='image/png')

# @app.route('/username')
# def user():
#     return session.get('username')

#APIs

#logging in 
@app.route('/api/login', methods=['POST'])
def verify_login():
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
            # cursor.execute('SELECT display_name FROM profile WHERE user_id = ?', (session['user_id'],))
            # username = cursor.fetchone()
            # default setting: the browser cookie is permanent
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

#signing up (request membership)
@app.route('/api/signup', methods=['POST'])
def save_login():
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
            
            # cursor.execute('SELECT id FROM logins WHERE email = ?', (email,))
            # user_id = cursor.fetchone()
            # session['user_id'] = int(user_id[0])
            # cursor.execute('SELECT display_name FROM profile WHERE user_id = ?', (session['user_id'],))
            # username = cursor.fetchone()
            # session['username'] = username
            # # default setting: the browser cookie is non-permanent, user will log out when browser is closed
            # session.permanent = True
            conn.commit()
            conn.close()

            return jsonify({'status': 'success'})
        except sqlite3.IntegrityError:
                return jsonify({'status': 'fail', 'message': 'Email already registered'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/saveprofile', methods=['POST'])
def save_profile():
    try:
        if 'user_id' in session:
            data = request.json
            conn = sqlite3.connect('dnd.db')
            cursor = conn.cursor()
            display_n = data['display_name']
            bio = data['bio']
            cursor.execute('SELECT 1 FROM profile WHERE user_id = ?', (session.get('user_id'),))
            profile_exists = cursor.fetchone()
            if profile_exists:
                cursor.execute('''
                    UPDATE profile 
                    SET display_name = ?, bio = ?
                    WHERE user_id = ?
                ''', (display_n, bio, session.get('user_id')))
            else:
                cursor.execute('''
                    INSERT INTO profile (user_id, display_name, bio)
                    VALUES (?, ?, ?)
                ''', (session.get('user_id'), display_n, bio))
            conn.commit()
            conn.close()
            return jsonify({'status': 'success'})
        else:
            return jsonify({'status':'fail','message':'unauthenticated'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
@app.route('/api/getprofile', methods=['GET'])
def get_profile():
    try:
        if 'user_id' in session:
            conn = sqlite3.connect('dnd.db')
            cursor = conn.cursor()
            cursor.execute('SELECT display_name, bio FROM profile WHERE user_id = ?', (session['user_id'],))
            # One because it matches only 1 profile
            row = cursor.fetchone()
            u_profile = {}
            if not row:
                # u_profile['exists'] = False
                cursor.execute('SELECT email FROM logins WHERE id = ?', (session.get('user_id'),))
                display_name = cursor.fetchone()
                u_profile['display_name'] = display_name
                u_profile['bio'] = "I'm a DND player at HGHS!"
            else:
                # u_profile['exists'] = True
                u_profile['display_name'] = row[0]
                u_profile['bio'] = row[1]
            conn.close()
            return jsonify({'status': 'success', 'profile': u_profile})
        else:
            return jsonify({'status':'fail','message':'unauthenticated'})
    except Exception as e:
        return jsonify({'status': 'fail', 'message': str(e)}), 500


#logout
@app.route('/api/logout', methods=['POST'])
def user_logout():
    try:
        print(session.get('user_id'))
        session.pop('user_id') 
        print(session.get('user_id'))
        return jsonify({'status':'success'})
    except Exception as e:
        return jsonify({'status':'fail', 'message':str(e)})

#checking session ID
@app.route('/api/sessionID', methods=['GET'])
def check_sessionID():
    if 'user_id' in session:
        return jsonify({'active': True})
    else:
        return jsonify({'active': False})
    

#checking admin status (specifically for notices)
@app.route('/api/admin', methods=['GET'])
def admin_check():
    print('hi')
    if 'user_id' in session:
        print('hi')
        conn = sqlite3.connect('dnd.db')
        cursor = conn.cursor()
        # admin_idlist = []
        cursor.execute('SELECT id FROM logins WHERE role = ?', ("admin",))
        adminIDs = cursor.fetchall()
        print(adminIDs)
        print('hi')
        for a_id in adminIDs:
            if session.get('user_id') == a_id[0]:
                print('hi')
                return jsonify({'admin': True})
        return jsonify({'admin': False})
    else:
        return jsonify({'admin': False})

#dice
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
            print(data)
            conn = sqlite3.connect('dnd.db')
            cursor = conn.cursor()
            name = data.get('name')
            info = json.dumps(data.get('info'))
            stats = json.dumps(data.get('stats'))
            print(info)  
            print(stats)
            print(session['user_id'])
            # try:
            cursor.execute('''
                INSERT INTO charsheets (user_id, name, info, stats)
                VALUES (?, ?, ?, ?)
            ''', (session['user_id'], name, info, stats))
            conn.commit()
            conn.close()
            return jsonify({'status': 'success'})
        else:
            print('die')
            return jsonify({'status':'fail','message':'unauthenticated'})
    except Exception as e:
        return jsonify({'status': 'fail', 'message' :str(e)}), 500
    

@app.route('/api/getchars', methods=['GET'])
def get_chars():
    try:
        conn = sqlite3.connect('dnd.db')
        cursor = conn.cursor()
        #if the user hasnt created a profile, it will default to their email (the case ensures that their name isnt completely ignored)
        cursor.execute('''SELECT logins.id, 
                    CASE
                        WHEN profile.display_name IS NULL THEN logins.email
                        ELSE profile.display_name
                    END AS display_name, c.name, c.info, c.stats 
                    FROM charsheets c 
                    JOIN logins ON logins.id = c.user_id
                    LEFT JOIN profile ON profile.user_id = c.user_id 
                    ORDER BY display_name ASC 
                ''')
        rows = cursor.fetchall()
        if 'user_id' in session:
            all_characters = []
            user_characters = []
            for c in rows:
                if c[0] == session.get('user_id'):
                    user_characters.append({'name': c[2], 'info': json.loads(c[3]), 'stats': json.loads(c[4])})
                else:
                    all_characters.append({'user': c[1], 'name': c[2], 'info': json.loads(c[3]), 'stats': json.loads(c[4])})
            conn.close()
            return jsonify({'status': 'success', 'signedin': True, 'all_c': all_characters, 'user_c': user_characters})
        else:
            all_characters = []
            for c in rows:
                all_characters.append({'user': c[1], 'name': c[2], 'info': json.loads(c[3]), 'stats': json.loads(c[4])})
            conn.close()
            return jsonify({'status': 'success', 'signedin': False, 'all_c': all_characters})

    except Exception as e:
        return jsonify({'status': 'fail', 'message': str(e)}), 500

#notes
@app.route('/api/savenotes', methods=['POST'])
def save_notes():
    try:
        if 'user_id' in session:
            data = request.json
            conn = sqlite3.connect('dnd.db')
            cursor = conn.cursor()
            date = data.get('date')   
            body = data.get('body')
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
            cursor.execute('SELECT date, notes FROM notes WHERE user_id = ? ORDER BY date DESC', (session['user_id'],))
            # print(cursor.fetchall())
            rows = cursor.fetchall()
            print(rows)
            notes = []
            for r in rows:
                notes.append({'date': r[0], 'notes': r[1]})
            
            conn.close()
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
                INSERT INTO notices (title, body, date, user_id)
                VALUES (?, ?, ?, ?)
            ''', (title, body, date, session['user_id']))
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
            return jsonify({'status':"fail",'message':'unauthenticated'})
        conn = sqlite3.connect('dnd.db')
        cursor = conn.cursor()
        cursor.execute('''
            IF EXISTS (SELECT * from notices)
                SELECT 
                    notices.title, 
                    notices.body, 
                    notices.date, 
                    logins.email
                FROM notices 
                JOIN logins ON notices.user_id = logins.id
                ORDER BY notices.date DESC
            ELSE
                SELECT 'No notices'
        ''')
        table = cursor.fetchall()
        print(table)
        notices = []
        if table == "No notices":
            notices = table
            print(notices)
        else:
            for row in table():
                notice = {'title': row[0], 'body': row[1], 'date':row[2], 'author':row[3]}
                notices.append(notice)
        return jsonify({'status': "success", "notices": notices})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/savetimetable', methods=['POST'])
def save_timetable():
    try:
        if 'user_id' in session:
            data = request.json
            conn = sqlite3.connect('dnd.db')
            cursor = conn.cursor()
            days = data.get('days')
            print(days) 
            cursor.execute('''
                UPDATE timetable 
                SET active_days = ?
            ''', (days,))
            conn.commit()
            conn.close()
            return jsonify({'status': 'success'})
        else:
            return jsonify({'status':'fail','message':'unauthenticated'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/gettimetable', methods=['GET'])
def get_timetable():
    try:
        conn = sqlite3.connect('dnd.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT active_days FROM timetable 
        ''')
        active_days = cursor.fetchone()
        if len(active_days) == 0:
            active_days = []
        return jsonify({'status': "success", "active_days": active_days})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/saveevent', methods=['POST'])
def save_event():
    try:
        if 'user_id' in session:
            data = request.json
            conn = sqlite3.connect('dnd.db')
            cursor = conn.cursor()
            date = data.get('date') 
            title = data.get('title')
            body = data.get('body')
            cursor.execute('''
                INSERT INTO event (user_id, title, body, date)
                VALUES (?, ?, ?, ?)
            ''', (session['user_id']), title, body, date)
            conn.commit()
            conn.close()
            return jsonify({'status': 'success'})
        else:
            return jsonify({'status':'fail','message':'unauthenticated'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/getevents', methods=['GET'])
def get_events():
    try:
        conn = sqlite3.connect('dnd.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT date, title, body 
            FROM event 
            ORDER BY date DESC
        ''')
        # print(cursor.fetchall())
        rows = cursor.fetchall()
        print(rows)
        events = []
        for r in rows:
            events.append({'date': r[0], 'title': r[1], 'body':r[2]})
        conn.close()
        return jsonify({'status': 'success', 'events': events})
    except Exception as e:
        return jsonify({'status': 'fail', 'message': str(e)}), 500


# functions defined after this line DO NOT RUN do NOT define a function after this
if __name__ == '__main__':
    app.run(debug=True)