from flask import Blueprint, render_template, request, redirect, url_for, session
import sqlite3
from functools import wraps

dashboard_bp = Blueprint('dashboard', __name__)

# Database setup
conn = sqlite3.connect('livegood.db')
conn.execute('''
    CREATE TABLE IF NOT EXISTS livegood_accounts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user INTEGER NOT NULL,
        livegood_username TEXT NOT NULL,
        livegood_password TEXT NOT NULL,
        FOREIGN KEY(user) REFERENCES users(id),
        UNIQUE(user, livegood_username, livegood_password)
    )
''')
conn.commit()
conn.close()

@dashboard_bp.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if request.method=='GET':
        if session['user_id'] in (None, ''):
            session['user_id']= None
            return redirect(url_for('auth.login'))
        user_id = session['user_id']
        with sqlite3.connect('livegood.db') as conn:
            cursor = conn.execute('SELECT * FROM livegood_accounts WHERE user = ?', [user_id])
            accounts = cursor.fetchall()
            return render_template('dashboard.html', accounts=accounts)
    
    if request.method == 'POST':
        if not session.get('user_id'):
            return redirect(url_for('auth.login'))
        user_id = session['user_id']
        username = request.form['username']
        password = request.form['password']
        if not username or not password:
            return render_template('dashboard.html', message="Invalid Arguments", status="error")
        with sqlite3.connect('livegood.db') as conn:
            try:
                conn.execute('INSERT INTO livegood_accounts (user, livegood_username, livegood_password) VALUES (?,?,?)', [user_id,username,password])
                conn.commit()
                message = 'Successfully Added!'
                status = 'success'
            except sqlite3.IntegrityError:
                message = "These credentials already exist!"
                status = 'error'
            except Exception:
                message = "Oops, Try again!"
                status = 'error'
            finally:
                accounts = conn.execute('SELECT * FROM livegood_accounts WHERE user = ?', [user_id]).fetchall()
                return render_template('dashboard.html', accounts=accounts, message=message, status=status)

        
@dashboard_bp.route('/deletelivegoodaccount', methods=['GET', 'POST'])
def deletelivegoodaccount():
    if request.method == 'POST':
        if session['user_id'] in (None, ''):
            session['user_id']= None
            return redirect(url_for('auth.login'))
        user_id = session['user_id']
        with sqlite3.connect('livegood.db') as conn: 
            try:
                id = request.form['id']
                cursor = conn.execute('DELETE FROM livegood_accounts WHERE id=?', [id])
                conn.commit()
                message = "Successfully Deleted"
                status = "success"
            except Exception as e:
                message = "Oops, Try again!"
                status = "error"
            finally:
                cursor = conn.execute('SELECT * FROM livegood_accounts WHERE user = ?', [user_id])
                accounts = cursor.fetchall()
                return render_template('dashboard.html', accounts=accounts, message=message, status=status)

@dashboard_bp.route('/updatelivegoodaccount', methods=['GET', 'POST'])
def updatelivegoodaccount():
    if request.method == 'POST':
        if session['user_id'] in (None, ''):
            session['user_id']= None
            return redirect(url_for('auth.login'))
        user_id = session['user_id']
        with sqlite3.connect('livegood.db') as conn: 
            try:
                id = request.form['id']
                livegood_username = request.form['livegood_username']
                livegood_password = request.form['livegood_password']
                if not id or not livegood_username or not livegood_password:
                    return render_template('dashboard.html', message="Invalid Arguments", status="error")
                cursor = conn.execute('UPDATE livegood_accounts SET livegood_username=?, livegood_password=? WHERE id=?', [livegood_username, livegood_password, id])
                conn.commit()
                message = "Successfully Updated"
                status = "success"
            except Exception as e:
                message = "Oops, Try again!"
                status = "error"
            finally:
                cursor = conn.execute('SELECT * FROM livegood_accounts WHERE user = ?', [user_id])
                accounts = cursor.fetchall()
                return render_template('dashboard.html', accounts=accounts, message=message, status=status)
