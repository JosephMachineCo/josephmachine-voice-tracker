#!/usr/bin/env python3
"""
Sales Visit Tracking App - Backend Server with AI Voice & Polishing
A Flask-based API for managing sales rep visits with authentication, OpenAI TTS, and GPT-4o-mini polishing
"""

from flask import Flask, request, jsonify, send_from_directory, Response
from flask_cors import CORS
import sqlite3
import hashlib
import secrets
import os
from datetime import datetime, timedelta
import json
from openai import OpenAI

app = Flask(__name__, static_folder='.')
CORS(app)

# Database setup
DB_PATH = 'sales_visits.db'
SECRET_KEY = os.environ.get('SECRET_KEY', secrets.token_hex(32))
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

def init_db():
    """Initialize database with required tables"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        manager_email TEXT NOT NULL,
        full_name TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    # Sessions table for authentication
    c.execute('''CREATE TABLE IF NOT EXISTS sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        token TEXT UNIQUE NOT NULL,
        expires_at TIMESTAMP NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )''')

    # Visits table
    c.execute('''CREATE TABLE IF NOT EXISTS visits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        visit_date DATE NOT NULL,
        customer_name TEXT NOT NULL,
        contact_name TEXT NOT NULL,
        location TEXT,
        latitude REAL,
        longitude REAL,
        discussion_summary TEXT,
        next_steps TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )''')

    conn.commit()
    conn.close()
    print("Database initialized successfully")

def hash_password(password):
    """Simple password hashing"""
    return hashlib.sha256(password.encode()).hexdigest()

def verify_token(token):
    """Verify authentication token and return user_id"""
    if not token:
        return None

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''SELECT user_id FROM sessions
                 WHERE token = ? AND expires_at > ?''',
              (token, datetime.now()))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None

def polish_answer(raw_text, question):
    """Use GPT-4o-mini to clean up and polish the voice transcript"""
    if not client:
        return raw_text  # Return original if no API key

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a professional assistant helping clean up voice transcripts from sales call notes. Fix typos, improve grammar, make it professional and clear, but keep the original meaning and content. Keep it concise."},
                {"role": "user", "content": f"Question: {question}\n\nRaw voice transcript: {raw_text}\n\nPlease clean this up to be professional and error-free:"}
            ],
            temperature=0.3,
            max_tokens=500
        )
        polished = response.choices[0].message.content.strip()
        return polished
    except Exception as e:
        print(f"Error polishing text: {e}")
        return raw_text  # Fallback to original

@app.route('/')
def index():
    """Serve the main application page"""
    return send_from_directory('.', 'index.html')

@app.route('/api/register', methods=['POST'])
def register():
    """Register a new sales rep"""
    data = request.json
    email = data.get('email', '').lower().strip()
    password = data.get('password')
    manager_email = data.get('manager_email', '').lower().strip()
    full_name = data.get('full_name', '')

    if not email or not password or not manager_email:
        return jsonify({'error': 'Email, password, and manager email are required'}), 400

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    try:
        c.execute('''INSERT INTO users (email, password_hash, manager_email, full_name)
                     VALUES (?, ?, ?, ?)''',
                  (email, hash_password(password), manager_email, full_name))
        conn.commit()
        user_id = c.lastrowid

        # Create session token
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(days=30)
        c.execute('INSERT INTO sessions (user_id, token, expires_at) VALUES (?, ?, ?)',
                  (user_id, token, expires_at))
        conn.commit()

        return jsonify({
            'success': True,
            'token': token,
            'email': email,
            'manager_email': manager_email,
            'full_name': full_name
        })
    except sqlite3.IntegrityError:
        return jsonify({'error': 'Email already registered'}), 400
    finally:
        conn.close()

@app.route('/api/login', methods=['POST'])
def login():
    """Login existing sales rep"""
    data = request.json
    email = data.get('email', '').lower().strip()
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute('SELECT id, password_hash, manager_email, full_name FROM users WHERE email = ?', (email,))
    result = c.fetchone()

    if not result or result[1] != hash_password(password):
        conn.close()
        return jsonify({'error': 'Invalid email or password'}), 401

    user_id, _, manager_email, full_name = result

    # Create session token
    token = secrets.token_urlsafe(32)
    expires_at = datetime.now() + timedelta(days=30)
    c.execute('INSERT INTO sessions (user_id, token, expires_at) VALUES (?, ?, ?)',
              (user_id, token, expires_at))
    conn.commit()
    conn.close()

    return jsonify({
        'success': True,
        'token': token,
        'email': email,
        'manager_email': manager_email,
        'full_name': full_name
    })

@app.route('/api/profile', methods=['GET'])
def get_profile():
    """Get user profile information"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    user_id = verify_token(token)

    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT email, manager_email, full_name FROM users WHERE id = ?', (user_id,))
    result = c.fetchone()
    conn.close()

    if not result:
        return jsonify({'error': 'User not found'}), 404

    return jsonify({
        'email': result[0],
        'manager_email': result[1],
        'full_name': result[2]
    })

@app.route('/api/polish', methods=['POST'])
def polish_text():
    """Polish a voice transcript using GPT-4o-mini"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    user_id = verify_token(token)

    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.json
    raw_text = data.get('text', '')
    question = data.get('question', '')

    if not raw_text:
        return jsonify({'error': 'Text is required'}), 400

    polished = polish_answer(raw_text, question)

    return jsonify({
        'original': raw_text,
        'polished': polished
    })

@app.route('/api/synthesize', methods=['POST'])
def synthesize_speech():
    """Generate natural speech using OpenAI TTS"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    user_id = verify_token(token)

    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401

    if not client:
        return jsonify({'error': 'OpenAI API key not configured'}), 500

    data = request.json
    text = data.get('text', '')

    if not text:
        return jsonify({'error': 'Text is required'}), 400

    try:
        response = client.audio.speech.create(
            model="tts-1",
            voice="alloy",  # Natural, neutral voice
            input=text
        )

        # Stream the audio response
        def generate():
            for chunk in response.iter_bytes(chunk_size=4096):
                yield chunk

        return Response(generate(), mimetype='audio/mpeg')
    except Exception as e:
        print(f"Error generating speech: {e}")
        return jsonify({'error': 'Failed to generate speech'}), 500

@app.route('/api/visits', methods=['POST'])
def submit_visit():
    """Submit a new customer visit"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    user_id = verify_token(token)

    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401

    data = request.json
    required_fields = ['visit_date', 'customer_name', 'contact_name']

    for field in required_fields:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute('''INSERT INTO visits
                 (user_id, visit_date, customer_name, contact_name, location,
                  latitude, longitude, discussion_summary, next_steps)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
              (user_id, data['visit_date'], data['customer_name'],
               data['contact_name'], data.get('location', ''),
               data.get('latitude'), data.get('longitude'),
               data.get('discussion_summary', ''), data.get('next_steps', '')))

    visit_id = c.lastrowid
    conn.commit()
    conn.close()

    return jsonify({
        'success': True,
        'visit_id': visit_id,
        'message': 'Visit recorded successfully'
    })

@app.route('/api/visits', methods=['GET'])
def get_visits():
    """Get all visits for the logged-in user"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    user_id = verify_token(token)

    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute('''SELECT id, visit_date, customer_name, contact_name, location,
                 latitude, longitude, discussion_summary, next_steps, created_at
                 FROM visits WHERE user_id = ?
                 ORDER BY visit_date DESC, created_at DESC''', (user_id,))

    visits = [dict(row) for row in c.fetchall()]
    conn.close()

    return jsonify(visits)

@app.route('/api/visits/all', methods=['GET'])
def get_all_visits():
    """Get all visits (for managers/admins)"""
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    user_id = verify_token(token)

    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    c = conn.cursor()

    c.execute('''SELECT v.id, v.visit_date, v.customer_name, v.contact_name,
                 v.location, v.latitude, v.longitude, v.discussion_summary,
                 v.next_steps, v.created_at, u.email, u.full_name, u.manager_email
                 FROM visits v
                 JOIN users u ON v.user_id = u.id
                 ORDER BY v.visit_date DESC, v.created_at DESC''')

    visits = [dict(row) for row in c.fetchall()]
    conn.close()

    return jsonify(visits)

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'openai_configured': client is not None}), 200

if __name__ == '__main__':
    print("Starting Joseph Machine Voice Visit Tracker with AI...")
    if not OPENAI_API_KEY:
        print("WARNING: OPENAI_API_KEY not set. AI features will be disabled.")
    init_db()
    port = int(os.environ.get('PORT', 10000))
    print(f"Server starting on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
