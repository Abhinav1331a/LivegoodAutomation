from collections import OrderedDict
from datetime import datetime
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

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
    earned_pay_period_column = driver.find_element(By.XPATH, "/html/body/div[8]/div/div[2]/div/section/div[2]/table/tbody/tr[2]/td/section/div/table/tbody/tr[2]/td[1]")
    earned_duration_column = driver.find_element(By.XPATH, "/html/body/div[8]/div/div[2]/div/section/div[2]/table/tbody/tr[2]/td/section/div/table/tbody/tr[2]/td[2]")
    # wait.until(EC.visibility_of_element_located((By.XPATH, '/html/body/div[8]/div/div[2]/div/section/div[2]/table/tbody/tr[2]/td/section/div/table/tbody/tr[2]/td[4]')))
    earned_value_column = driver.find_element(By.XPATH, "/html/body/div[8]/div/div[2]/div/section/div[2]/table/tbody/tr[2]/td/section/div/table/tbody/tr[2]/td[4]")

    # Get the values of the 2nd and 4th columns
    earned_value = earned_value_column.text
    earned_duration_value = earned_duration_column.text
    earned_pay_period = earned_pay_period_column.text
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
        # print(date_string)
        users_ordered_by_date.setdefault(date_string, []).append((user, rank))
    
    # sort the keys by their corresponding date values
    sorted_keys = []
    for key in users_ordered_by_date.keys():
        try:
            date = datetime.strptime(key, '%Y-%m-%d').date()
            sorted_keys.append((key, date))
        except ValueError:
            # Skip the key if it doesn't match the format
            continue

    sorted_keys.sort(key=lambda x: x[1])
    sorted_keys = [key for key, date in sorted_keys]

    # create a new ordered dictionary with the sorted keys
    users_ordered_by_date = OrderedDict((key, users_ordered_by_date[key]) for key in sorted_keys)
    return users_ordered_by_date