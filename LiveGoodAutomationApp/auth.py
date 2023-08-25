from flask import Blueprint, flash, get_flashed_messages, render_template, request, redirect, url_for, session
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
                flash("Signup failed!", category='message')
                flash("error", category='status')
                return redirect(url_for('auth.signup'))
                # return render_template('signup.html', message="Signup failed!", status="error")
        
        flash("Signup successful!", category='message')
        flash("success", category='status')
        return redirect(url_for('auth.login'))
        # return render_template('login.html', message="Signup successful!", status="success")
    
    if request.method == "GET":
        flash_messages = get_flashed_messages(with_categories=True)
        message=None
        status=None
        for category, msg in flash_messages:
            if category == 'message':
                message = msg
            elif category == 'status':
                status = msg
        return render_template('signup.html', message=message, status=status)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        flash("Already logged in!", category='message')
        flash("success", category='status')
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
                    flash("Successfully logged in!", category='message')
                    flash("success", category='status')
                    return redirect(url_for('dashboard.dashboard')) 
                    # return render_template('dashboard.html', message="Successfully logged in!", status="success")
                else:
                    flash("Invalid credentials, try again!", category='message')
                    flash("error", category='status')
                    return redirect(url_for('auth.login')) 
                    # return render_template('login.html', message='Invalid credentials, try again!', status = "error")
            except:
                flash("Login Failed!", category='message')
                flash("error", category='status')
                return redirect(url_for('auth.login'))
                # return render_template('login.html', message="Login Failed!", status="error")
    
    if request.method=="GET":
        flash_messages = get_flashed_messages(with_categories=True)
        message=None
        status=None
        for category, msg in flash_messages:
            if category == 'message':
                message = msg
            elif category == 'status':
                status = msg
        return render_template('login.html', message=message, status=status)

@auth_bp.route('/logout')
def logout():
    session.pop('user_id', None)
    flash("Successfully logged out!", category='message')
    flash("success", category='status')
    return redirect(url_for('auth.login'))


def login_required(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            flash("Session timed out. Login again!", category='message')
            flash("error", category='status')
            return redirect(url_for('auth.login'))
        return view_func(*args, **kwargs)
    return wrapper