# backend.py
import json
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException
from selenium.webdriver.common.action_chains import ActionChains
import time

USER_DATA_FILE = "user_data.json"

def initialize_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Run in headless mode to not open a browser window
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def save_user_data(data):
    with open(USER_DATA_FILE, 'w') as file:
        json.dump(data, file)

def load_user_data():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, 'r') as file:
            return json.load(file)
    return None

def fill_form(driver, wait, permit_number, last_name, dob_month, dob_day, dob_year, zip_code):
    # Open the DMV road test scheduler page
    driver.get("https://www.ri.gov/app/dmv/road_tests")
    
    # Wait for the page to load and ensure the first input field is present
    print("got")
    permit_input = wait.until(EC.presence_of_element_located((By.NAME, 'permit_number')))

    # Fill in the form with user details
    permit_input.send_keys(permit_number)
    driver.find_element(By.NAME, 'last_name').send_keys(last_name)
    driver.find_element(By.NAME, 'date_of_birth_month').send_keys(dob_month)
    driver.find_element(By.NAME, 'date_of_birth_day').send_keys(dob_day)
    driver.find_element(By.NAME, 'date_of_birth_year').send_keys(dob_year)
    driver.find_element(By.NAME, 'zip_code').send_keys(zip_code)
    
    # Wait for the submit button to be clickable, then click it
    submit_button = wait.until(EC.element_to_be_clickable((By.ID, 'continue')))
    ActionChains(driver).move_to_element(submit_button).click().perform()
    print("logged in")
    
    # Wait for the verification page to load and click the positive button
    continue_button = wait.until(EC.element_to_be_clickable((By.ID, 'continue')))
    ActionChains(driver).move_to_element(continue_button).click().perform()
    print("verification continued")
    
    # Wait for the dashboard page to load and click the reschedule appointment link
    reschedule_button = wait.until(EC.element_to_be_clickable((By.ID, 'reschedule_appt')))
    ActionChains(driver).move_to_element(reschedule_button).click().perform()
    print("reschedule appointment clicked")

def find_first_available_date(driver, wait, course_name):
    try:
        # Get the current month being displayed
        current_month = driver.find_element(By.XPATH, '//header[contains(@class, "calendar-header")]//span').text
        # Find all rows in the calendar
        for i in range(1, 6):  # Loop through each row (assumed 5 rows)
            for j in range(1, 8):  # Loop through each column (7 days a week)
                try:
                    date_element = driver.find_element(By.XPATH, f'/html/body/div[1]/div[2]/div/div/div/div[2]/div/div/fieldset/h4/div/div/table/tbody/tr[{i}]/td[{j}]/a')
                    if date_element:
                        print(f"First available date found for {course_name} in {current_month}: {date_element.get_attribute('id')}")
                        return f"First available date found for {course_name} in {current_month}: {date_element.get_attribute('id')}"
                except (NoSuchElementException, StaleElementReferenceException):
                    continue
        # If no date is found, go to the next month
        print(f"No available dates found for {course_name} in {current_month}, trying next month...")
        try:
            next_month_button = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div[2]/div/div/div/div[2]/div/div/fieldset/h4/div/div/header/a[2]')))
            ActionChains(driver).move_to_element(next_month_button).click().perform()
            time.sleep(2)  # Give time for the page to load after clicking next month
            return find_first_available_date(driver, wait, course_name)
        except TimeoutException:
            print(f"Timed out trying to click next month for {course_name}.")
    except TimeoutException:
        print(f"Timed out waiting for available dates for {course_name}.")
        return None

def check_skills_course_a(permit_number, last_name, dob_month, dob_day, dob_year, zip_code):
    # Save user data for future use
    save_user_data({
        "permit_number": permit_number,
        "last_name": last_name,
        "dob_month": dob_month,
        "dob_day": dob_day,
        "dob_year": dob_year,
        "zip_code": zip_code
    })

    driver = initialize_driver()
    try:
        wait = WebDriverWait(driver, 30)
        fill_form(driver, wait, permit_number, last_name, dob_month, dob_day, dob_year, zip_code)
        
        # Wait for the location selection page to load and select Skills Course A
        try:
            course_a_button = wait.until(EC.element_to_be_clickable((By.ID, 'continue_select_loc_20')))
            ActionChains(driver).move_to_element(course_a_button).click().perform()
            print("Skills Course A selected")
            # Find the first available date for Course A
            course_a_date = find_first_available_date(driver, wait, "Skills Course A")
            if course_a_date:
                return course_a_date
        except TimeoutException:
            print("Skills Course A not available.")
    finally:
        driver.quit()

def check_skills_course_b(permit_number, last_name, dob_month, dob_day, dob_year, zip_code):
    driver = initialize_driver()
    try:
        wait = WebDriverWait(driver, 30)
        fill_form(driver, wait, permit_number, last_name, dob_month, dob_day, dob_year, zip_code)
        
        # Navigate back to the location selection page and select Skills Course B
        driver.get("https://www.ri.gov/app/dmv/road_tests/citizens/locations")
        try:
            course_b_button = wait.until(EC.element_to_be_clickable((By.ID, 'continue_select_loc_21')))
            ActionChains(driver).move_to_element(course_b_button).click().perform()
            print("Skills Course B selected")
            # Find the first available date for Course B
            course_b_date = find_first_available_date(driver, wait, "Skills Course B")
            if course_b_date:
                return course_b_date
        except TimeoutException:
            print("Skills Course B not available.")
    finally:
        driver.quit()

def check_both_courses(permit_number, last_name, dob_month, dob_day, dob_year, zip_code):
    course_a_result = check_skills_course_a(permit_number, last_name, dob_month, dob_day, dob_year, zip_code)
    course_b_result = check_skills_course_b(permit_number, last_name, dob_month, dob_day, dob_year, zip_code)
    return course_a_result, course_b_result
