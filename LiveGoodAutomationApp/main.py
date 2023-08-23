from datetime import datetime
import json
from flask import Flask
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import logging
import functions_framework
from http import HTTPStatus
import chromedriver_binary 

app = Flask(__name__)
logger = logging.getLogger()
logger.setLevel(logging.WARN)

def login(driver, wait, username, password):
    # Open the webpage in the background
    # driver.set_window_position(-10000, 0)
    driver.get("https://livegood.com/login")
    wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="home"]/div/form/div[3]/div[1]/button')))

    # Find the username and password fields and enter the credentials
    username_field = driver.find_element(By.XPATH, '//*[@id="home"]/div/form/div[1]/input')
    password_field = driver.find_element(By.XPATH, '//*[@id="password"]')
    wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="home"]/div/form/div[1]/input')))
    wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="password"]')))
    username_field.send_keys(username)
    password_field.send_keys(password)

    # Find and click the login button
    login_button = driver.find_element(By.XPATH, '//*[@id="home"]/div/form/div[3]/div[1]/button')
    wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="home"]/div/form/div[3]/div[1]/button')))
    login_button.click()

def getEarnings(driver, wait):
    wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="slide-menu"]/div/div[1]/ul/li[13]/a')))
    

    # print("LATEST ROW: ", latest_row)
    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            # Perform the operation that may raise a TimeoutException
            driver.get("https://www.livegood.com/bo/earnings")
            wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[8]/div/div[2]/div/section/div[2]/table/tbody/tr[2]/td/section/div/table/tbody')))
            break  # If the operation is successful, break out of the loop
        except TimeoutException:
            if attempt == max_attempts - 1:  # If this is the last attempt, re-raise the exception
                raise
            else:
                print(f"TimeoutException occurred, retrying (attempt {attempt + 1} of {max_attempts})")
    # Get the 1st, 2nd and 4th columns in the row
    earned_pay_period = driver.find_element(By.XPATH, "/html/body/div[8]/div/div[2]/div/section/div[2]/table/tbody/tr[2]/td/section/div/table/tbody/tr[2]/td[1]")
    earned_duration_column = driver.find_element(By.XPATH, "/html/body/div[8]/div/div[2]/div/section/div[2]/table/tbody/tr[2]/td/section/div/table/tbody/tr[2]/td[2]")
    # wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[8]/div/div[2]/div/section/div[2]/table/tbody/tr[2]/td/section/div/table/tbody/tr[2]/td[4]')))
    earned_value_column = driver.find_element(By.XPATH, "/html/body/div[8]/div/div[2]/div/section/div[2]/table/tbody/tr[2]/td/section/div/table/tbody/tr[2]/td[4]")

    # Get the values of the 2nd and 4th columns
    earned_value = earned_value_column.text
    earned_duration_value = earned_duration_column.text
    return earned_value, earned_duration_value, earned_pay_period

def getRank(driver, wait):
    driver.get("https://www.livegood.com/bo/rank")
    wait.until(EC.visibility_of_element_located((By.XPATH, '//*[@id="rankChart"]/div/div/h3')))

        # this will be in format "CURRENT RANK Gold"
    current_rank = driver.find_element(By.XPATH, '//*[@id="rankChart"]/div/div/h3').text.split("CURRENT RANK ")[1].strip()
    return current_rank

def getSubscribedUsersExpiryInfo(driver, wait):
    max_attempts = 3
    for attempt in range(max_attempts):
        try:
                # Perform the operation that may raise a TimeoutException
            driver.get("https://www.livegood.com/bo/matrixTree")
            wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[8]/div/div[2]/div/section/div[2]/center/center/table/tbody')))
            break  # If the operation is successful, break out of the loop
        except TimeoutException:
            if attempt == max_attempts - 1:  # If this is the last attempt, re-raise the exception
                raise
            else:
                print(f"TimeoutException occurred, retrying (attempt {attempt + 1} of {max_attempts})")
    users_table = driver.find_element(By.XPATH, '/html/body/div[8]/div/div[2]/div/section/div[2]/center/center/table')
    rows =  users_table.find_elements(By.TAG_NAME, 'tr')

    users_ordered_by_date = {}

    for row in rows[1:]:
            # get date from 4th column
        background_color = row.value_of_css_property('background-color')
            # print(background_color)
        rank = "Unranked"
        if background_color == "rgba(242, 167, 125, 1)":
            rank = "Bronze"
        elif background_color == "rgba(183, 183, 183, 1)":
            rank = "Silver"
        elif background_color == "rgba(145, 186, 224, 1)":
            rank = "Platinum"
        elif background_color == "rgba(255, 255, 59, 1)":
            rank = "Gold"
        elif background_color == "rgba(0, 29, 83, 1)":
            rank = "Diamond"
        else:
            rank = "Unranked"    
        user = row.find_element(By.XPATH, './td[2]').text
        date_string = row.find_element(By.XPATH, './td[5]').text
            # date = datetime.strptime(date_string, '%Y-%m-%d').date()
        users_ordered_by_date.setdefault(date_string, []).append((user, rank))
    return users_ordered_by_date

@app.route('/getStatistics')
def getStatistics(request):
    # Handle preflight requests for CORS
    if request.method == 'OPTIONS':
            headers = {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Max-Age': '3600'
            }
            return ('', 204, headers)

    # Set CORS headers for the main request
    headers = {
        'Access-Control-Allow-Origin': '*'
    }

    if request.method == 'POST':
        request_json = request.get_json()
        # Check if required inputs are there
        if not request_json or 'username' not in request_json or 'password' not in request_json:
            return (json.dumps({'message': 'username, password of LiveGood are required. Invalid Arguments.'}), HTTPStatus.BAD_REQUEST, headers)

        # Define the username and password (case sensitive)
        username = request_json['username']
        password = request_json['password']

        # Check if format of the input are valid
        if username in (None, "") or password in (None, ""):
            return (json.dumps({'message': 'username, password of LiveGood should not be empty or null. Invalid Format.'}), HTTPStatus.BAD_REQUEST, headers)

        # Create Options
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--window-size=1920,1080")

        # Create a webdriver instance (you may need to specify the path to the driver executable)
        driver = webdriver.Chrome(options=options)

        # Wait for the login to complete and go to the earnings page
        wait = WebDriverWait(driver, 10)

        try:
            # Login
            login(driver, wait, username, password)
            
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

            # Formulate return object
            result = {}
            result["Username"] = username
            result[earned_pay_period] = (earned_duration_value ,earned_value)
            result["Rank"] = current_rank
            result['Users'] = users_ordered_by_date
            

            return (json.dumps(result), HTTPStatus.OK, headers)
        except TimeoutException as e:
            logger.log(logging.ERROR, "Failed due to %s", e)
            try:
                login_failed_text = driver.find_element(By.XPATH, '/html/body/div[6]/div/section/div/div/div/table/tbody/tr/td[1]/font/nobr').text
                if login_failed_text.lower().strip() == "login failed:":
                    return (json.dumps({"message": "Login Failed! Invalid Credentails"}), HTTPStatus.NOT_ACCEPTABLE, headers)
            except NoSuchElementException:
                pass
            return (json.dumps({"earned_value": "Try again later!"}), HTTPStatus.INTERNAL_SERVER_ERROR, headers)
        
if __name__ == '__main__':
    app.debug = True
    app.run()
            