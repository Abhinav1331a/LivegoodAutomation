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
        # print(user_id)
        conn = sqlite3.connect('livegood.db')
        cursor = conn.execute('SELECT * FROM livegood_accounts WHERE user = ?', [user_id])
        accounts = cursor.fetchall()
        conn.close()
        # return accounts
        # context = {}
        # context['accounts'] = accounts 
        # print("accounts:", context) 
        return render_template('dashboard.html', accounts=accounts)
    if request.method == 'POST':
        try:
            if session['user_id'] in (None, ''):
                session['user_id']= None
                return redirect(url_for('auth.login'))
            user_id = session['user_id']
            username = request.form['username']
            password = request.form['password']
            if username in (None, '') or password in (None, ''):
                return render_template('dashboard.html', message="Invalid Arguments")
            conn = sqlite3.connect('livegood.db')
            cursor = conn.execute('INSERT INTO livegood_accounts (user, livegood_username, livegood_password) VALUES (?,?,?)', [user_id,username,password])
            conn.commit()
            message = 'Successfully Added!'
        except sqlite3.IntegrityError as e:
            message = "These credentials already exist!"
        except Exception as e:
            message = "Oops, Try again!"
        finally:
            cursor = conn.execute('SELECT * FROM livegood_accounts WHERE user = ?', [user_id])
            accounts = cursor.fetchall()
            conn.close()
            return render_template('dashboard.html', accounts=accounts, message=message)

@dashboard_bp.route('/deletelivegoodaccount', methods=['GET', 'POST'])
def deletelivegoodaccount():
    if request.method == 'POST':
        if session['user_id'] in (None, ''):
            session['user_id']= None
            return redirect(url_for('auth.login'))
        user_id = session['user_id']
        try:
            id = request.form['id']
            conn = sqlite3.connect('livegood.db')
            cursor = conn.execute('DELETE FROM livegood_accounts WHERE id=?', [id])
            conn.commit()
            message = "Successfully Deleted"
        except Exception as e:
            message = "Oops, Try again!"
        finally:
            cursor = conn.execute('SELECT * FROM livegood_accounts WHERE user = ?', [user_id])
            accounts = cursor.fetchall()
            conn.close()
            return render_template('dashboard.html', accounts=accounts, message=message)
