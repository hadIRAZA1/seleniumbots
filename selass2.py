from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
import time
import traceback
import logging # Import logging to configure external loggers
from file_logger import get_logger # Import your custom logger factory

BASE_URL = "https://seeqlo-dev.vercel.app"

# Initialize your script-specific logger at the module level
logger = get_logger(script_name="FullAssignmentCreator")

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
        logger.error(f"❌ An error occurred during login: {e}", extra={'screenshot': screenshot_path})
        logger.error(traceback.format_exc()) # Log the full traceback
        raise

def create_full_assignment(driver):
    """
    Navigates to My Desk, creates a new assignment, and fills out the form.
    """
    wait = WebDriverWait(driver, 30)

    try:
        # 1. Click on "My Desk" sidebar option
        logger.info("\n🖥️ Navigating to 'My Desk' section...")
        my_desk_span = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//span[contains(@class, 'ml-3') and contains(@class, 'text-sm') and contains(text(), 'My Desk')]")
        ))
        my_desk_span.click()
        logger.info("✅ Clicked on My Desk sidebar link.")
        time.sleep(2)

        # 2. Click the "Create Assignment" tab/button
        logger.info("\n📝 Clicking 'Create Assignment' tab...")
        create_assignment_tab = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(text(), 'Create Assignment')]")
        ))
        create_assignment_tab.click()
        logger.info("✅ Clicked 'Create Assignment' tab.")
        
        # Give some time for the content to load after tab click
        time.sleep(3) 

        # 3. Click the large purple "Create Assignment +" button
        logger.info("\n➕ Clicking the large 'Create Assignment +' button...")
        large_create_assignment_btn = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[span[text()='Create Homework'] and span[text()='+']]")
        ))
        large_create_assignment_btn.click()
        logger.info("✅ Clicked large 'Create Homework +' button using precise XPath.")

        # Increased sleep time for the new form to fully load
        logger.info("⏳ Waiting for new assignment form to load...")
        time.sleep(5) 

        # 4. Fill out the Assignment Form

        # Select "Taha's Class" checkbox
        logger.info("\n☑️ Selecting 'Taha's Class' checkbox...")
        taha_class_checkbox_locator = (By.XPATH, "//div[./div/div/span[contains(text(), \"Taha's Class\")]]/div[contains(@class, 'rounded-md') and contains(@class, 'border-2')]")
        
        taha_class_checkbox = wait.until(EC.visibility_of_element_located(taha_class_checkbox_locator))
        wait.until(EC.element_to_be_clickable(taha_class_checkbox_locator)).click()
        logger.info("✅ Selected 'Taha's Class' checkbox.")
        time.sleep(0.5)

        # Skip "Assignment Title" - no action needed

        # Select Grade 1 from the "Grade" dropdown
        logger.info("\n📚 Selecting Grade 1...")
        grade_dropdown_element = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//label[contains(text(), 'Grade')]/following-sibling::select")
        ))
        grade_dropdown = Select(grade_dropdown_element)
        grade_dropdown.select_by_visible_text("1st Grade")
        logger.info("✅ Selected 1st Grade.")
        time.sleep(0.5)

        # Select Maths from the "Subject" dropdown
        logger.info("\n📐 Selecting Subject: Maths...")
        subject_dropdown_element = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//label[contains(text(), 'Subject')]/following-sibling::select")
        ))
        subject_dropdown = Select(subject_dropdown_element)
        subject_dropdown.select_by_visible_text("Maths")
        logger.info("✅ Selected Subject: Maths.")
        time.sleep(0.5)

        # Select Number from the "Unit" dropdown
        logger.info("\n🔢 Selecting Unit: Number...")
        unit_dropdown_element = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//label[contains(text(), 'Unit')]/following-sibling::select")
        ))
        unit_dropdown = Select(unit_dropdown_element)
        unit_dropdown.select_by_visible_text("Number")
        logger.info("✅ Selected Unit: Number.")
        time.sleep(0.5)

        # Write "whole number" in the Description field
        logger.info("\n✍️ Entering Description...")
        description_textarea = wait.until(EC.presence_of_element_located(
            (By.XPATH, "//label[contains(text(), 'Description')]/following-sibling::textarea")
        ))
        description_textarea.send_keys("whole number")
        logger.info("✅ Entered 'whole number' in description.")
        time.sleep(0.5)

        # Select the "Multiple Choice" checkbox
        logger.info("\n☑️ Selecting 'Multiple Choice' checkbox...")
        mcq_checkbox = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//span[contains(text(), 'Multiple Choice')]//preceding-sibling::input[@type='checkbox']")
        ))
        mcq_checkbox.click()
        logger.info("✅ Selected 'Multiple Choice'.")
        time.sleep(0.5)

        # Click "Generate with AI"
        logger.info("\n💡 Clicking 'Generate with AI'...")
        generate_ai_btn = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(text(), 'Generate with AI')]")
        ))
        generate_ai_btn.click()
        logger.info("✅ Clicked 'Generate with AI'.")

        logger.info("⏳ Waiting for AI generation and pressing END key to scroll down the modal...")
        # Find the main modal content container that is scrollable
        modal_content_locator = (By.XPATH, "//div[@role='dialog']//div[contains(@class, 'relative') and contains(@class, 'transform') and contains(@class, 'bg-white')]")
        
        try:
            modal_content_element = wait.until(EC.presence_of_element_located(modal_content_locator))
            logger.info("Found modal content element for scrolling.")
            
            actions = ActionChains(driver)

            for _ in range(7):
                actions.send_keys_to_element(modal_content_element, Keys.END).perform()
                time.sleep(1.4)
            logger.info("✅ Modal scrolled to bottom using Keys.END via ActionChains.")
        except TimeoutException:
            logger.warning("⚠️ Warning: Modal content element not found for scrolling within timeout. Proceeding without specific modal scrolling.")
        except Exception as e:
            logger.error(f"❌ Error during modal scrolling: {e}")
            logger.error(traceback.format_exc())

        # --- UPDATED: Explicitly wait for the file upload div to become invisible ---
        intercepting_div_locator = (By.XPATH, "//div[contains(@class, 'border-2') and contains(@class, 'border-dashed') and contains(@class, 'border-gray-300') and contains(text(), 'Click to upload')]")
        try:
            logger.info("⏳ Waiting for intercepting file upload div to become invisible...")
            wait.until(EC.invisibility_of_element_located(intercepting_div_locator))
            logger.info("✅ Intercepting file upload div is now invisible.")
        except TimeoutException:
            logger.warning("⚠️ Warning: Intercepting file upload div did not become invisible within timeout (10 seconds). Proceeding anyway.")
            driver.save_screenshot("intercepting_dropdown_still_visible.png")


        # Click the final "Create Assignment" button at the bottom using native click
        logger.info("\n🎉 Clicking final 'Create Assignment' button...")
        final_create_assignment_btn = wait.until(EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(text(), 'Send Homework') and contains(@class, 'bg-gradient-to-r')]")
        ))

        final_create_assignment_btn.click()
        logger.info("✅ Final 'Create Assignment' clicked.")
        time.sleep(3) # Short sleep after clicking to allow navigation

    except Exception as e:
        screenshot_path = "selenium_full_assignment_error.png"
        driver.save_screenshot(screenshot_path)
        logger.error(f"❌ An error occurred during assignment creation: {e}", extra={'screenshot': screenshot_path})
        logger.error(traceback.format_exc()) # Log the full traceback
        raise

def main():
    """Main function to initialize Selenium and run the automation."""
    driver = None
    
    # Configure external loggers to suppress verbose output
    logging.getLogger('webdriver_manager').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)

    try:
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        driver.maximize_window()

        email = "ibadt@gmail.com"
        password = "ibad1234"

        login(driver, email, password)
        create_full_assignment(driver)

        logger.info("\n🎯 Automation script finished successfully.")

    except Exception as e:
        logger.critical(f"❌ A critical error occurred and the script stopped: {e}")
        logger.critical(traceback.format_exc()) # Log the critical traceback
    finally:
        if driver:
            logger.info("👋 Closing the browser in 5 seconds...")
            time.sleep(5)
            driver.quit()

if __name__ == "__main__":
    main()