from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pickle
import json
import time
import os

def setup_driver():

    chrome_options = Options()
    
    profile_dir = os.path.join(os.getcwd(), "uber_chrome_profile")
    if not os.path.exists(profile_dir):
        os.makedirs(profile_dir)
        
    chrome_options.add_argument(f"user-data-dir={profile_dir}")
    
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Chrome(options=chrome_options)
    
    return driver

def login_to_uber(driver):

    driver.get("https://auth.uber.com/login")
    
    print("Please log in manually to your Uber account.")
    print("The script will continue automatically after you log in.")
    print("Waiting for the user to complete login...")
    

    current_url = driver.current_url
    
    max_wait_time = 300  # 5 minutes
    wait_interval = 5  # Check every 5 seconds
    total_waited = 0
    
    while driver.current_url == current_url and total_waited < max_wait_time:
        time.sleep(wait_interval)
        total_waited += wait_interval
        print(f"Still waiting for login... ({total_waited} seconds elapsed)")
    
    if total_waited >= max_wait_time:
        print("Timeout waiting for login. Please try again.")
        return False
    
    print("Login detected! Proceeding to collect cookies.")
    return True

def collect_cookies(driver):

    selenium_cookies = driver.get_cookies()
    
    requests_cookies = {}
    for cookie in selenium_cookies:
        requests_cookies[cookie['name']] = cookie['value']
    
    return requests_cookies

def save_cookies(cookies, filename="uber_cookies.json"):

    with open(filename, 'w') as f:
        json.dump(cookies, f, indent=4)
    
    print(f"Cookies saved to {filename}")

def main():

    print("Starting Uber cookie collector")
    print("------------------------------")
    
    driver = setup_driver()
    
    try:
        if login_to_uber(driver):
            time.sleep(5)
            
            cookies = collect_cookies(driver)
            
            save_cookies(cookies)
            
            print(f"Successfully collected {len(cookies)} cookies.")
            print("You can now use these cookies with the requests library.")
            
            with open('uber_cookies.pkl', 'wb') as f:
                pickle.dump(cookies, f)
            print("Cookies also saved in pickle format for easier loading in Python.")
    
    except Exception as e:
        print(f"An error occurred: {str(e)}")
    
    finally:
        print("Closing browser...")
        driver.quit()

if __name__ == "__main__":
    main() 