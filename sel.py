from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import time
import traceback
import logging # Ensure logging module is imported for getLogger
from file_logger import get_logger # Import the new logger

BASE_URL = "https://seeqlo-dev.vercel.app"

# Initialize the logger for this specific script
logger = get_logger(script_name="Spelling Bee Assignment")

def login(driver, email, password):
    """Navigates to the login page and logs the user in using Selenium."""
    try:
        logger.info("▶ Starting login process...")
        driver.get(BASE_URL + "/login")
        wait = WebDriverWait(driver, 20)

        logger.info("✉ Entering email...")
        email_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[contains(@placeholder, 'example.com')]")))
        email_input.send_keys(email)

        logger.info("🔑 Entering password...")
        password_input = driver.find_element(By.XPATH, "//input[@type='password']")
        password_input.send_keys(password)

        logger.info("-> Clicking login button...")
        login_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Log in')]")))
        login_btn.click()

        logger.info("🔐 Logged in, waiting for dashboard to load...")
        wait.until(EC.url_changes(BASE_URL + "/login"))
        wait.until(EC.presence_of_element_located((By.XPATH, "//h1[normalize-space(.)='Welcome back, ibadt']")))
        logger.info("✅ Login successful, dashboard loaded.")

    except Exception as e:
        screenshot_path = "selenium_login_error.png"
        driver.save_screenshot(screenshot_path)
        logger.error(f"An error occurred during login: {e}", extra={'screenshot': screenshot_path})
        traceback.print_exc()
        raise

def create_assignment(driver):
    """Navigates to assignment creation and selects options using Selenium."""
    wait = WebDriverWait(driver, 30)

    try:
        logger.info("\n🖥️ Navigating to 'My Desk' section...")
        my_desk_span = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//span[contains(@class, 'ml-3') and contains(@class, 'text-sm') and contains(text(), 'My Desk')]")
        ))
        my_desk_span.click()
        logger.info("✅ Clicked on My Desk sidebar link.")
        time.sleep(2)

        logger.info("\n🐝 Clicking on 'Spelling Bee' activity...")
        spelling_bee = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//div[contains(@class, 'cursor-pointer')]//div[contains(., 'Spelling Bee')]")
        ))
        spelling_bee.click()
        logger.info("✅ Clicked on Spelling Bee activity.")
        time.sleep(2)

        logger.info("\n🔎 Handling 'Class' dropdown...")
        try:
            class_dropdown_element = wait.until(EC.presence_of_element_located(
                (By.XPATH, '//select[contains(@class, "w-full") and (./option[contains(text(), "-- Select Class --")] or ./option[contains(text(), "math grade 5 (2 students)")])]')
            ))
            class_dropdown = Select(class_dropdown_element)
            class_dropdown.select_by_visible_text("math grade 5 (2 students)")
            logger.info("🎓 Class 'math grade 5 (2 students)' selected successfully.")
        except Exception as e:
            screenshot_path = "class_selection_error.png"
            driver.save_screenshot(screenshot_path)
            logger.error(f"Could not select class: {e}", extra={'screenshot': screenshot_path})
            raise

        time.sleep(1)

        logger.info("\n🔎 Handling 'Difficulty' dropdown...")
        try:
            difficulty_dropdown_element = wait.until(EC.presence_of_element_located(
                (By.XPATH, '//select[contains(@class, "w-full") and (./option[contains(text(), "-- Select Difficulty --")] or ./option[contains(text(), "Grade 4-6 (Medium)")])]')
            ))
            difficulty_dropdown = Select(difficulty_dropdown_element)
            difficulty_dropdown.select_by_visible_text("Grade 4-6 (Medium)")
            logger.info("📘 Difficulty 'Grade 4-6 (Medium)' selected successfully.")
        except Exception as e:
            screenshot_path = "difficulty_selection_error.png"
            driver.save_screenshot(screenshot_path)
            logger.error(f"Could not select difficulty: {e}", extra={'screenshot': screenshot_path})
            raise

        time.sleep(1)

        logger.info("\n🚀 Clicking 'Assign to Class' button...")
        assign_btn = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(text(), 'Assign to Class')]")
        ))
        assign_btn.click()
        logger.info("✅ Assignment successfully created!")
        time.sleep(3)

    except Exception as e:
        screenshot_path = "selenium_assignment_error.png"
        driver.save_screenshot(screenshot_path)
        logger.error(f"An error occurred during assignment creation: {e}", extra={'screenshot': screenshot_path})
        traceback.print_exc()
        raise

def main():
    """Main function to initialize Selenium and run the automation."""
    driver = None
    try:
        # Configure external loggers to suppress verbose output
        logging.getLogger('webdriver_manager').setLevel(logging.WARNING)
        logging.getLogger('urllib3').setLevel(logging.WARNING)

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        driver.maximize_window()
        email = "ibadt@gmail.com"
        password = "ibad1234"
        login(driver, email, password)
        create_assignment(driver)
        logger.info("🎯 Automation script finished successfully.", extra={'status': 'COMPLETED'})

    except Exception as e:
        logger.error(f"A critical error occurred and the script stopped: {e}", extra={'status': 'FAILED'})
        traceback.print_exc()
    finally:
        if driver:
            logger.info("👋 Closing the browser...")
            time.sleep(5)
            driver.quit()

if __name__ == "__main__":
    main()
