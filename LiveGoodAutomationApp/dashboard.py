import subprocess
import sys
from flask import Blueprint, flash, get_flashed_messages, render_template, request, redirect, url_for, session
import sqlite3
from functools import wraps
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
import logging
from http import HTTPStatus
from LiveGoodAutomationApp.helper import * 
import chromedriver_binary

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
            message = None
            status = None
            flash_messages = get_flashed_messages(with_categories=True)
            for category, msg in flash_messages:
                if category == 'message':
                    message = msg
                elif category == 'status':
                    status = msg
            return render_template('dashboard.html', accounts=accounts, message=message, status=status)
    
    if request.method == 'POST':
        if not session.get('user_id'):
            return redirect(url_for('auth.login'))
        user_id = session['user_id']
        username = request.form['username']
        password = request.form['password']
        if not username or not password:
            flash("Invalid Arguments", category='message')
            flash("error", category='status')
            return redirect(url_for('dashboard.dashboard'))        
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
                # accounts = conn.execute('SELECT * FROM livegood_accounts WHERE user = ?', [user_id]).fetchall()
                flash(message, category='message')
                flash(status, category='status')
                return redirect(url_for('dashboard.dashboard'))  
                # return render_template('dashboard.html', accounts=accounts, message=message, status=status)

        
@dashboard_bp.route('/deletelivegoodaccount', methods=['POST'])
def deletelivegoodaccount():
    if request.method == 'POST':
        if session['user_id'] in (None, ''):
            session['user_id']= None
            return redirect(url_for('auth.login'))
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
                # cursor = conn.execute('SELECT * FROM livegood_accounts WHERE user = ?', [user_id])
                # accounts = cursor.fetchall()
                flash(message, category='message')
                flash(status, category='status')
                return redirect(url_for('dashboard.dashboard'))  
                # return render_template('dashboard.html', accounts=accounts, message=message, status=status)

@dashboard_bp.route('/updatelivegoodaccount', methods=['POST'])
def updatelivegoodaccount():
    if request.method == 'POST':
        if session['user_id'] in (None, ''):
            session['user_id']= None
            return redirect(url_for('auth.login'))
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
                # cursor = conn.execute('SELECT * FROM livegood_accounts WHERE user = ?', [user_id])
                # accounts = cursor.fetchall()
                flash(message, category='message')
                flash(status, category='status')
                return redirect(url_for('dashboard.dashboard'))  
                # return render_template('dashboard.html', accounts=accounts, message=message, status=status)

@dashboard_bp.route('/detailedstats', methods=['POST'])
def detailedstats():
    if request.method == "POST":
        if session['user_id'] in (None, ''):
            session['user_id']= None
            return redirect(url_for('auth.login'))
        user_id = session['user_id']
        with sqlite3.connect('livegood.db') as conn:
            try:
                livegood_username = request.form['livegood_username']
                livegood_password = request.form['livegood_password']
                # Check if format of the input are valid
                if livegood_username in (None, "") or livegood_password in (None, ""):
                    flash("Username, Password of LiveGood should not be empty or null. Invalid Format.", category='message')
                    flash("error", category='status')
                    return redirect(url_for('dashboard.dashboard'))  
                    # return render_template('dashboard.html', message='Username, Password of LiveGood should not be empty or null. Invalid Format.', status="error")

                # Create Options
                options = Options()
                options.add_argument("--no-sandbox")
                options.add_argument("--disable-gpu")
                options.add_argument("--disable-dev-shm-usage")
                options.add_argument("--headless")
                options.add_argument("--window-size=1920,1080")

                # Create a webdriver instance (you may need to specify the path to the driver executable)
                try:
                    driver = webdriver.Chrome(options=options)
                except WebDriverException as e:
                    print(f"Error: {e}")
                    # Update ChromeDriver
                    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', '--force-reinstall', 'chromedriver-binary-auto'])
                    # Reinitialize the driver
                    driver = webdriver.Chrome(options=options)

                # Wait for the login to complete and go to the earnings page
                wait = WebDriverWait(driver, 5)

            
                # Login
                login(driver, wait, livegood_username, livegood_password)
                
                # Get Earnings
                earned_value, earned_duration_value, earned_pay_period = getEarnings(driver, wait)
                print("EARNINGS: ", earned_value, earned_duration_value, earned_pay_period)

                # Get Rank
                current_rank = getRank(driver, wait)
                print("RANK: ", current_rank)

                # Get Subscribed Users Expiry Info
                users_ordered_by_date = getSubscribedUsersExpiryInfo(driver, wait)
                
                # Close the driver
                driver.quit()              

                # Store results in session accross users id to allow simulataneous exec.
                data = {}
                data['username'] = livegood_username
                data['earned_pay_period'] = earned_pay_period
                data['earned_duration_value'] = earned_duration_value
                data['earned_value'] = earned_value
                data['rank'] = current_rank
                data['users'] = users_ordered_by_date

                # Using session id and session to implement PRG(Post Redirect Get) arch.
                session_key = str(session['user_id'])+"stats"
                session[session_key] = data

                # Redirect to results page
                return redirect(url_for('dashboard.results'))
            
            except TimeoutException as e:
                logging.error("Failed due to %s", e)
                cursor = conn.execute('SELECT * FROM livegood_accounts WHERE user = ?', [user_id])
                accounts = cursor.fetchall()
                try:
                    login_failed_text = driver.find_element(By.XPATH, '/html/body/div[6]/div/section/div/div/div/table/tbody/tr/td[1]/font/nobr').text
                    if login_failed_text.lower().strip() == "login failed:":
                        flash("Login Failed! Invalid LiveGood Credentails", category='message')
                        flash("error", category='status')
                        return redirect(url_for('dashboard.dashboard'))  
                        # return render_template("dashboard.html", accounts=accounts, message="Login Failed! Invalid LiveGood Credentails",status="error")
                except NoSuchElementException:
                    flash("Oops! Try again later.", category='message')
                    flash("error", category='status')
                    return redirect(url_for('dashboard.dashboard'))  
                    # return render_template("dashboard.html", accounts=accounts, message="Try again later!",status="error")
            except Exception as e:
                    logging.error("Failed due to %s", e)
                    # cursor = conn.execute('SELECT * FROM livegood_accounts WHERE user = ?', [user_id])
                    # accounts = cursor.fetchall()
                    # message = "Oops, Try again!"
                    # status = "error"
                    flash("Oops! Try again later.", category='message')
                    flash("error", category='status')
                    return redirect(url_for('dashboard.dashboard')) 
                    # return render_template('dashboard.html', accounts=accounts, message=message, status=status)

@dashboard_bp.route('/results')
def results():
    if request.method=="GET":
        # Retrieve data from session
        # Generate unique session key using session ID
        session_key = str(session['user_id'])+"stats"
        if session_key not in session:
            flash("Oops! Try again later.", category="message")
            flash("error", category="status")
            return redirect(url_for("dashboard.dashboard"))
        data = session.get(session_key)
        username = data['username']
        earned_pay_period = data['earned_pay_period']
        earned_duration_value = data['earned_duration_value']
        earned_value = data['earned_value']
        rank = data['rank']
        users = data['users']
        # Render template with data
        message=None
        status=None
        return render_template(
            'detailedStats.html',
            username=username,
            earned_pay_period=earned_pay_period,
            earned_duration_value=earned_duration_value,
            earned_value=earned_value,
            rank=rank,
            users=users,
            message=message,
            status=status
        )