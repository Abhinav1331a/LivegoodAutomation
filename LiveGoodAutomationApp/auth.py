from flask import Blueprint, render_template, request, redirect, url_for, session
import sqlite3
from functools import wraps

auth_bp = Blueprint('auth', __name__)

# Database setup
conn = sqlite3.connect('livegood.db')
conn.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    )
''')
conn.commit()
conn.close()

@auth_bp.route('/')
def home():
    return redirect(url_for('auth.login'))

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        with sqlite3.connect('livegood.db') as conn:
            try: 
                conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
                conn.commit()
            except:
                return render_template('signup.html', message="Signup failed!", status="error")

        return render_template('login.html', message="Signup successful!", status="success")
    if request.method == "GET":
        return render_template('signup.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard.dashboard'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        with sqlite3.connect('livegood.db') as conn:
            try:
                cursor = conn.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
                user = cursor.fetchone()
                if user:
                    session['user_id'] = user[0]
                    return render_template('dashboard.html', message="Successfully logged in!", status="success")
                else:
                    return render_template('login.html', message='Invalid credentials, try again!', status = "error")
            except:
                return render_template('login.html', message="Login Failed!", status="error")
    
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('auth.login'))


def login_required(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return view_func(*args, **kwargs)
    return wrapper