from flask import Flask, render_template, request, jsonify, session, redirect, url_for, send_from_directory, send_file
from flask_cors import CORS
import sqlite3
from datetime import datetime
import hashlib
import os
from functools import wraps
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__, 
            static_folder=BASE_DIR,
            static_url_path='',
            template_folder=BASE_DIR)
app.secret_key = 'hackathon_hub_secret_key_2024'
CORS(app)

def init_db():
    conn = sqlite3.connect('hackathon_hub.db')
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_type TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS students (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER UNIQUE NOT NULL,
        name TEXT NOT NULL,
        dob TEXT NOT NULL,
        mobile TEXT NOT NULL,
        whatsapp TEXT NOT NULL,
        email TEXT NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS organizations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER UNIQUE NOT NULL,
        organization_name TEXT NOT NULL,
        phone TEXT NOT NULL,
        email TEXT NOT NULL,
        address TEXT NOT NULL,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS hackathons (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        organization_id INTEGER NOT NULL,
        hackathon_name TEXT NOT NULL,
        date_time TEXT NOT NULL,
        location TEXT NOT NULL,
        latitude REAL,
        longitude REAL,
        description TEXT NOT NULL,
        organizer_name TEXT NOT NULL,
        contact_details TEXT NOT NULL,
        prize_details TEXT NOT NULL,
        num_rounds INTEGER NOT NULL,
        round_details TEXT NOT NULL,
        problem_statement_type TEXT NOT NULL,
        team_size_min INTEGER NOT NULL,
        team_size_max INTEGER NOT NULL,
        food_stay_available INTEGER DEFAULT 0,
        registration_closed INTEGER DEFAULT 0,
        poster_url TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(organization_id) REFERENCES organizations(id)
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS teams (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        hackathon_id INTEGER NOT NULL,
        team_name TEXT NOT NULL,
        team_leader_id INTEGER NOT NULL,
        food_stay TEXT,
        problem_statement TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(hackathon_id) REFERENCES hackathons(id),
        FOREIGN KEY(team_leader_id) REFERENCES students(id)
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS team_members (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        team_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        mobile TEXT NOT NULL,
        whatsapp TEXT NOT NULL,
        email TEXT NOT NULL,
        dob TEXT NOT NULL,
        college TEXT NOT NULL,
        degree TEXT NOT NULL,
        department TEXT NOT NULL,
        year TEXT NOT NULL,
        FOREIGN KEY(team_id) REFERENCES teams(id)
    )''')
    
    conn.commit()
    conn.close()

init_db()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    if 'user_id' not in session:
        return send_from_directory(BASE_DIR, 'index.html')
    return send_from_directory(BASE_DIR, 'index.html')

@app.route('/index.html')
def index_html():
    return send_from_directory(BASE_DIR, 'index.html')

@app.route('/styles.css')
def styles():
    return send_from_directory(BASE_DIR, 'styles.css')

@app.route('/script.js')
def scripts():
    return send_from_directory(BASE_DIR, 'script.js')

@app.route('/robot.png')
def serve_robot():
    return send_file(r"C:\Users\ranji\.gemini\antigravity\brain\e9a134cf-d446-4f38-9c4a-8d5f2759938f\robot_assistant_1777177744652.png")

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        data = request.json
        user_type = data.get('user_type')
        email = data.get('email')
        password = data.get('password')
        confirm_password = data.get('confirm_password')
        
        if password != confirm_password:
            return jsonify({'error': 'Passwords do not match'}), 400
        
        try:
            conn = sqlite3.connect('hackathon_hub.db')
            c = conn.cursor()
            
            hashed_password = hash_password(password)
            c.execute('INSERT INTO users (user_type, email, password) VALUES (?, ?, ?)',
                     (user_type, email, hashed_password))
            conn.commit()
            user_id = c.lastrowid
            
            if user_type == 'student':
                name = data.get('name')
                dob = data.get('dob')
                mobile = data.get('mobile')
                whatsapp = data.get('whatsapp')
                
                c.execute('''INSERT INTO students (user_id, name, dob, mobile, whatsapp, email)
                           VALUES (?, ?, ?, ?, ?, ?)''',
                         (user_id, name, dob, mobile, whatsapp, email))
            else:
                organization_name = data.get('organization_name')
                phone = data.get('phone')
                address = data.get('address')
                
                c.execute('''INSERT INTO organizations (user_id, organization_name, phone, email, address)
                           VALUES (?, ?, ?, ?, ?)''',
                         (user_id, organization_name, phone, email, address))
            
            conn.commit()
            conn.close()
            
            return jsonify({'success': True, 'message': 'Signup successful! Please login.'}), 201
        except sqlite3.IntegrityError:
            return jsonify({'error': 'Email already exists'}), 400
    
    return jsonify({'error': 'Method not allowed'}), 405

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.json
        email = data.get('email')
        password = data.get('password')
        
        conn = sqlite3.connect('hackathon_hub.db')
        c = conn.cursor()
        
        hashed_password = hash_password(password)
        c.execute('SELECT id, user_type FROM users WHERE email = ? AND password = ?',
                 (email, hashed_password))
        user = c.fetchone()
        conn.close()
        
        if user:
            session['user_id'] = user[0]
            session['user_type'] = user[1]
            session['email'] = email
            return jsonify({'success': True, 'user_type': user[1]}), 200
        else:
            return jsonify({'error': 'Invalid email or password'}), 401
    
    return jsonify({'error': 'Method not allowed'}), 405

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    user_id = session.get('user_id')
    user_type = session.get('user_type')
    
    conn = sqlite3.connect('hackathon_hub.db')
    c = conn.cursor()
    data = {}
    
    if user_type == 'student':
        c.execute('SELECT id, name FROM students WHERE user_id = ?', (user_id,))
        student = c.fetchone()
        data['student_name'] = student[1] if student else 'Student'
        
        c.execute('''SELECT DISTINCT h.id, h.hackathon_name, h.date_time, h.location, h.registration_closed
                   FROM hackathons h
                   JOIN teams t ON h.id = t.hackathon_id
                   LEFT JOIN team_members tm ON t.id = tm.team_id
                   WHERE tm.email = ? OR t.team_leader_id = ?''', 
                 (session['email'], student[0]))
        registered = c.fetchall()
        data['registered_hackathons'] = [
            {'id': h[0], 'name': h[1], 'datetime': h[2], 'location': h[3], 'registration_closed': h[4]} 
            for h in registered
        ]
    else:
        c.execute('SELECT id, organization_name FROM organizations WHERE user_id = ?', (user_id,))
        org = c.fetchone()
        data['organization_name'] = org[1] if org else 'Organization'
        data['organization_id'] = org[0] if org else None
        
        # Get scheduled hackathons
        if org:
            c.execute('''SELECT h.id, h.hackathon_name, h.date_time, h.location, h.registration_closed, COUNT(t.id) as teams_count
                       FROM hackathons h
                       LEFT JOIN teams t ON h.id = t.hackathon_id
                       WHERE h.organization_id = ?
                       GROUP BY h.id''', (org[0],))
            scheduled = c.fetchall()
            data['scheduled_hackathons'] = [
                {'id': h[0], 'name': h[1], 'datetime': h[2], 'location': h[3], 'registration_closed': h[4], 'teams': h[5]}
                for h in scheduled
            ]
    
    conn.close()
    
    return jsonify({
        'user_type': user_type,
        'data': data
    }), 200

@app.route('/api/hackathons', methods=['GET'])
@login_required
def get_hackathons():
    conn = sqlite3.connect('hackathon_hub.db')
    c = conn.cursor()
    
    c.execute('''SELECT h.id, h.hackathon_name, h.date_time, h.location, h.latitude, h.longitude,
                   h.description, h.organizer_name, h.contact_details, h.prize_details,
                   h.num_rounds, h.round_details, h.problem_statement_type, h.team_size_min,
                   h.team_size_max, h.food_stay_available, h.poster_url, h.registration_closed, o.organization_name
                FROM hackathons h
                JOIN organizations o ON h.organization_id = o.id
                ORDER BY h.date_time DESC''')
    
    hackathons = c.fetchall()
    conn.close()
    
    result = []
    for h in hackathons:
        result.append({
            'id': h[0],
            'name': h[1],
            'datetime': h[2],
            'location': h[3],
            'latitude': h[4],
            'longitude': h[5],
            'description': h[6],
            'organizer_name': h[7],
            'contact_details': h[8],
            'prize_details': h[9],
            'num_rounds': h[10],
            'round_details': h[11],
            'problem_statement_type': h[12],
            'team_size_min': h[13],
            'team_size_max': h[14],
            'food_stay_available': h[15],
            'poster_url': h[16],
            'registration_closed': h[17],
            'organization_name': h[18]
        })
    
    return jsonify(result), 200

@app.route('/api/hackathons', methods=['POST'])
@login_required
def create_hackathon():
    if session.get('user_type') != 'organization':
        return jsonify({'error': 'Only organizations can create hackathons'}), 403
    
    data = request.json
    user_id = session.get('user_id')
    
    conn = sqlite3.connect('hackathon_hub.db')
    c = conn.cursor()
    
    # Get organization ID
    c.execute('SELECT id FROM organizations WHERE user_id = ?', (user_id,))
    org = c.fetchone()
    
    if not org:
        return jsonify({'error': 'Organization not found'}), 404
    
    try:
        c.execute('''INSERT INTO hackathons 
                   (organization_id, hackathon_name, date_time, location, latitude, longitude,
                    description, organizer_name, contact_details, prize_details, num_rounds,
                    round_details, problem_statement_type, team_size_min, team_size_max,
                    food_stay_available, poster_url)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                 (org[0], data['hackathon_name'], data['date_time'], data['location'],
                  data.get('latitude'), data.get('longitude'), data['description'],
                  data['organizer_name'], data['contact_details'], data['prize_details'],
                  data['num_rounds'], data['round_details'], data['problem_statement_type'],
                  data['team_size_min'], data['team_size_max'],
                  1 if data.get('food_stay_available') else 0, data.get('poster_url')))
        
        conn.commit()
        hackathon_id = c.lastrowid
        conn.close()
        
        return jsonify({'success': True, 'hackathon_id': hackathon_id}), 201
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 400

@app.route('/api/teams', methods=['POST'])
@login_required
def register_team():
    if session.get('user_type') != 'student':
        return jsonify({'error': 'Only students can register teams'}), 403
    
    data = request.json
    hackathon_id = data.get('hackathon_id')
    user_id = session.get('user_id')
    
    conn = sqlite3.connect('hackathon_hub.db')
    c = conn.cursor()
    
    c.execute('SELECT id FROM students WHERE user_id = ?', (user_id,))
    student = c.fetchone()
    if not student:
        conn.close()
        return jsonify({'error': 'Student profile not found'}), 404
    team_leader_id = student[0]
    
    try:
        # Create team
        c.execute('''INSERT INTO teams (hackathon_id, team_name, team_leader_id, food_stay, problem_statement)
                   VALUES (?, ?, ?, ?, ?)''',
                 (hackathon_id, data['team_name'], team_leader_id,
                  data.get('food_stay'), data.get('problem_statement')))
        
        team_id = c.lastrowid
        
        # Add team members
        for member in data.get('team_members', []):
            c.execute('''INSERT INTO team_members 
                       (team_id, name, mobile, whatsapp, email, dob, college, degree, department, year)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                     (team_id, member['name'], member['mobile'], member['whatsapp'],
                      member['email'], member['dob'], member['college'],
                      member['degree'], member['department'], member['year']))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'team_id': team_id}), 201
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 400

@app.route('/api/hackathons/<int:hackathon_id>')
@login_required
def get_hackathon(hackathon_id):
    conn = sqlite3.connect('hackathon_hub.db')
    c = conn.cursor()
    
    c.execute('''SELECT h.id, h.hackathon_name, h.date_time, h.location, h.latitude, h.longitude,
                   h.description, h.organizer_name, h.contact_details, h.prize_details,
                   h.num_rounds, h.round_details, h.problem_statement_type, h.team_size_min,
                   h.team_size_max, h.food_stay_available, h.poster_url, h.organization_id,
                   h.registration_closed, o.organization_name
                FROM hackathons h
                JOIN organizations o ON h.organization_id = o.id
                WHERE h.id = ?''', (hackathon_id,))
    
    hackathon = c.fetchone()
    conn.close()
    
    if not hackathon:
        return jsonify({'error': 'Hackathon not found'}), 404
    
    return jsonify({
        'id': hackathon[0],
        'name': hackathon[1],
        'datetime': hackathon[2],
        'location': hackathon[3],
        'latitude': hackathon[4],
        'longitude': hackathon[5],
        'description': hackathon[6],
        'organizer_name': hackathon[7],
        'contact_details': hackathon[8],
        'prize_details': hackathon[9],
        'num_rounds': hackathon[10],
        'round_details': hackathon[11],
        'problem_statement_type': hackathon[12],
        'team_size_min': hackathon[13],
        'team_size_max': hackathon[14],
        'food_stay_available': hackathon[15],
        'poster_url': hackathon[16],
        'organization_id': hackathon[17],
        'registration_closed': hackathon[18],
        'organization_name': hackathon[19]
    }), 200

@app.route('/api/hackathons/<int:hackathon_id>', methods=['DELETE'])
@login_required
def delete_hackathon(hackathon_id):
    if session.get('user_type') != 'organization':
        return jsonify({'error': 'Only organizations can delete hackathons'}), 403
        
    user_id = session.get('user_id')
    
    conn = sqlite3.connect('hackathon_hub.db')
    c = conn.cursor()
    
    c.execute('SELECT id FROM organizations WHERE user_id = ?', (user_id,))
    org = c.fetchone()
    
    if not org:
        conn.close()
        return jsonify({'error': 'Organization not found'}), 404
        
    c.execute('SELECT organization_id FROM hackathons WHERE id = ?', (hackathon_id,))
    hackathon = c.fetchone()
    
    if not hackathon:
        conn.close()
        return jsonify({'error': 'Hackathon not found'}), 404
        
    if hackathon[0] != org[0]:
        conn.close()
        return jsonify({'error': 'Unauthorized to delete this hackathon'}), 403
        
    try:
        c.execute('DELETE FROM team_members WHERE team_id IN (SELECT id FROM teams WHERE hackathon_id = ?)', (hackathon_id,))
        c.execute('DELETE FROM teams WHERE hackathon_id = ?', (hackathon_id,))
        c.execute('DELETE FROM hackathons WHERE id = ?', (hackathon_id,))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Hackathon deleted successfully'}), 200
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 400

@app.route('/api/hackathons/<int:hackathon_id>/toggle_registration', methods=['PUT'])
@login_required
def toggle_registration(hackathon_id):
    if session.get('user_type') != 'organization':
        return jsonify({'error': 'Only organizations can toggle registration status'}), 403
        
    user_id = session.get('user_id')
    
    conn = sqlite3.connect('hackathon_hub.db')
    c = conn.cursor()
    
    c.execute('SELECT id FROM organizations WHERE user_id = ?', (user_id,))
    org = c.fetchone()
    
    if not org:
        conn.close()
        return jsonify({'error': 'Organization not found'}), 404
        
    c.execute('SELECT organization_id, registration_closed FROM hackathons WHERE id = ?', (hackathon_id,))
    hackathon = c.fetchone()
    
    if not hackathon:
        conn.close()
        return jsonify({'error': 'Hackathon not found'}), 404
        
    if hackathon[0] != org[0]:
        conn.close()
        return jsonify({'error': 'Unauthorized to modify this hackathon'}), 403
        
    new_status = 0 if hackathon[1] else 1
    
    try:
        c.execute('UPDATE hackathons SET registration_closed = ? WHERE id = ?', (new_status, hackathon_id))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'registration_closed': new_status}), 200
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 400

@app.route('/api/hackathons/<int:hackathon_id>/teams', methods=['GET'])
@login_required
def get_hackathon_teams(hackathon_id):
    if session.get('user_type') != 'organization':
        return jsonify({'error': 'Only organizations can view registered teams'}), 403
        
    user_id = session.get('user_id')
    
    conn = sqlite3.connect('hackathon_hub.db')
    c = conn.cursor()
    
    c.execute('SELECT id FROM organizations WHERE user_id = ?', (user_id,))
    org = c.fetchone()
    
    if not org:
        conn.close()
        return jsonify({'error': 'Organization not found'}), 404
        
    c.execute('SELECT organization_id FROM hackathons WHERE id = ?', (hackathon_id,))
    hackathon = c.fetchone()
    
    if not hackathon:
        conn.close()
        return jsonify({'error': 'Hackathon not found'}), 404
        
    if hackathon[0] != org[0]:
        conn.close()
        return jsonify({'error': 'Unauthorized to view teams for this hackathon'}), 403
        
    c.execute('''SELECT t.id, t.team_name, t.food_stay, t.problem_statement, 
                        s.name, s.email, s.mobile, s.whatsapp
                 FROM teams t
                 JOIN students s ON t.team_leader_id = s.id
                 WHERE t.hackathon_id = ?''', (hackathon_id,))
    teams = c.fetchall()
    
    result = []
    for t in teams:
        team_id = t[0]
        c.execute('''SELECT name, email, mobile, whatsapp, dob, college, degree, department, year
                     FROM team_members WHERE team_id = ?''', (team_id,))
        members = c.fetchall()
        
        member_list = []
        for m in members:
            member_list.append({
                'name': m[0],
                'email': m[1],
                'mobile': m[2],
                'whatsapp': m[3],
                'dob': m[4],
                'college': m[5],
                'degree': m[6],
                'department': m[7],
                'year': m[8]
            })
            
        result.append({
            'team_id': team_id,
            'team_name': t[1],
            'food_stay': t[2],
            'problem_statement': t[3],
            'leader': {
                'name': t[4],
                'email': t[5],
                'mobile': t[6],
                'whatsapp': t[7]
            },
            'members': member_list
        })
        
    conn.close()
    return jsonify(result), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)