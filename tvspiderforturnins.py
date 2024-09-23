#use selenium to open a website
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from datetime import date, timedelta
from selenium.webdriver.common.keys import Keys
import sys
from mpspider import MatterportSpider
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

class TalonViewAutomation:
    def __init__(self, driver, username, password):
        self.driver = driver
        self.username = username
        self.password = password

    @staticmethod
    def initialize_driver():
        chrome_options = webdriver.ChromeOptions()
        # Disable Chrome's pop-up asking for permissions
        chrome_options.add_experimental_option("prefs", {
            "profile.default_content_setting_values.clipboard": 1,  # Auto-allow clipboard access
            "profile.default_content_setting_values.notifications": 1,  # Auto-allow notifications
            "profile.default_content_setting_values.geolocation": 1  # Auto-allow geolocation if needed
        })
        driver = webdriver.Chrome(options=chrome_options)
        driver.get("https://mechanicalvisionsolutions.collaborate.center/")
        return driver

    def sign_in(self):
        username_field = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.ID, "Email"))
        )
        username_field.send_keys(self.username)

        password_field = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.ID, "Password"))
        )
        password_field.send_keys(self.password)

        sign_in_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.btn.btn-block.btn-lg.text-white.text-uppercase"))
        )
        sign_in_button.click()

    def select_session_and_assign_username(self, site_id):
        all_sessions_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//a[@href='/all-sessions']//p[contains(text(),'All Sessions')]"))
        )
        all_sessions_button.click()

        filters_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label='Show filters']"))
        )
        filters_button.click()

        date_range_input = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "input[placeholder='MM/DD/YYYY – MM/DD/YYYY']"))
        )
        date_range_input.click()

        today = date.today()
        start_date = today - timedelta(days=4)
        end_date = today + timedelta(days=1)

        date_range_input.clear()
        date_range_input.send_keys(f"{end_date.strftime('%m/%d/%Y')} – {start_date.strftime('%m/%d/%Y')}")
        date_range_input.send_keys(Keys.ENTER)
        date_range_input.send_keys(Keys.ESCAPE)

        search_bar = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='Search']"))
        )
        search_bar.clear()
        search_bar.send_keys(site_id)
        time.sleep(2)

        # Check if no results are found and adjust the date range
        try:
            checkbox = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.XPATH, f"//input[@type='checkbox' and contains(@class, 'PrivateSwitchBase-input')]"))
            )
        except Exception:
            print(f"No sessions found for {site_id}. Adjusting date range to go back another 4 days.")
            start_date = start_date - timedelta(days=4)
            date_range_input.clear()
            date_range_input.send_keys(f"{end_date.strftime('%m/%d/%Y')} – {start_date.strftime('%m/%d/%Y')}")
            date_range_input.send_keys(Keys.ENTER)
            date_range_input.send_keys(Keys.ESCAPE)

            # Retry finding the checkbox after adjusting the date range
            checkbox = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.XPATH, f"//input[@type='checkbox' and contains(@class, 'PrivateSwitchBase-input')]"))
            )

        parent_element = self.driver.execute_script("return arguments[0].closest('span');", checkbox)
        self.driver.execute_script("arguments[0].click();", parent_element)
        
        #add a step here that would prompt the user to skip this session at this point in the code and go to the next site id
        
        add_user_button = WebDriverWait(self.driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label='Switch owner of selected sessions']"))
        )
        add_user_button.click()

        username_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='Search name or email...']"))
        )
        username_input.clear()
        username_input.send_keys("john.james@talonalliance.io")

        john_james_element = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//div[@title='John james']"))
        )

        make_owner_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Make an owner')]"))
        )
        make_owner_button.click()

    def enter_initial_session(self):
        session_element = WebDriverWait(self.driver, 20).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".MuiCardMedia-root[data-active='true']"))
        )
        session_element.click()

    def display_folder_names(self):
        folder_elements = WebDriverWait(self.driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".session-folders-item .session-folders-item-name"))
        )
        folder_names = [folder.text for folder in folder_elements]
        for name in folder_names:
            print(name)

    def add_360(self):
        view_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), '360° View')]"))
        )
        view_button.click()

    def add_3d(self):
        model_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), '3D Model (ContextCapture)')]"))
        )
        model_button.click()

    def add_matterport(self):
        web_page_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Web Page')]"))
        )
        web_page_button.click()
    def add_matterport_confirm(self):
        add_web_page_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'MuiButton-outlinedPrimary')]//span[contains(text(), 'Add Web Page')]"))
        )
        add_web_page_button.click()

    def input_matterport_url(self):
        # Wait for the URL input field to be visible
        url_input = WebDriverWait(self.driver, 10).until(
            EC.visibility_of_element_located((By.ID, "url"))
        )

        # Get the Matterport URL from the clipboard (assuming it's already copied)
        matterport_url = self.driver.execute_script("return navigator.clipboard.readText()")

        # Clear the input field and enter the Matterport URL
        url_input.clear()
        url_input.send_keys(matterport_url)

        # You might need to add a delay here if the page needs time to process the URL

    def click_add_button(self):
        add_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div/div[2]/div[3]/div[2]/section[2]/div[3]/footer/div/div[1]/button"))
        )
        self.driver.execute_script("arguments[0].click();", add_button)

    def click_360_view_button(self):
        view_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//li[contains(@class, 'MuiMenuItem-root')]//span[contains(text(), '360° View')]"))
        )
        self.driver.execute_script("arguments[0].scrollIntoView(true);", view_button)
        self.driver.execute_script("arguments[0].click();", view_button)

    def click_add_folder_to_item_button(self, folder_name):
        # Use double quotes around the folder_name in the XPath expression to avoid issues with apostrophes
        add_folder_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, f"//span[contains(@class, 'session-folders-item-name') and normalize-space(text())=\"{folder_name}\"]/following-sibling::span[contains(@class, 'gallery-item-add-button')]"))
        )
        self.driver.execute_script("arguments[0].click();", add_folder_button)

    def click_done_button(self):
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//button[contains(@class, 'timeline-button-submit') and contains(text(), 'Done')]"))
        )
        
        done_buttons = self.driver.find_elements(By.XPATH, "//div[not(contains(@class, 'closed'))]//button[contains(@class, 'timeline-button-submit') and contains(text(), 'Done')]")
        
        if done_buttons:
            for button in done_buttons:
                if button.is_displayed() and button.is_enabled():
                    self.driver.execute_script("arguments[0].click();", button)
                    return
        
        done_buttons = self.driver.find_elements(By.XPATH, "//button[contains(@class, 'timeline-button-submit') and contains(text(), 'Done')]")
        for button in done_buttons:
            if button.is_displayed() and button.is_enabled():
                self.driver.execute_script("arguments[0].click();", button)
                return
        
        raise Exception("No clickable 'Done' button found")

    def is_360_present(self, flight_name):
        """
        Check if a 360° view with the given flight_name already exists.

        Args:
            flight_name (str): The name of the flight to check.

        Returns:
            bool: True if the 360° view exists, False otherwise.
        """
        try:
            # Locate all figcaption elements that represent 360° items
            figcaptions = WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, "figcaption"))
            )
            for fig in figcaptions:
                span = fig.find_element(By.CSS_SELECTOR, "span.gallery-item-span")
                title = span.get_attribute("title").strip().lower()
                if title == flight_name.lower():
                    print(f"360° view '{flight_name}' already exists.")
                    return True
            return False
        except Exception as e:
            print(f"Error while checking for existing 360° views: {e}")
            return False


def main():
    driver = TalonViewAutomation.initialize_driver()

    # Load credentials from environment variables
    myusername = os.getenv("TALONVIEW_USERNAME")
    mypassword = os.getenv("TALONVIEW_PASSWORD")
    
    talon_view = TalonViewAutomation(driver, myusername, mypassword)
    talon_view.sign_in()

    # Load Matterport credentials from environment variables
    matterport_username = os.getenv("MATTERPORT_USERNAME")
    matterport_password = os.getenv("MATTERPORT_PASSWORD")
    
    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[1])
    matterport_spider = MatterportSpider(matterport_username, matterport_password)
    matterport_spider.login()
    driver.switch_to.window(driver.window_handles[0])

    results = []

    while True:
        site_ids = input("Enter a list of site IDs separated by commas (or type 'exit' to quit): ").strip().split(',')

        if site_ids[0].lower() == 'exit':
            break

        for site_id in site_ids:
            site_id = site_id.strip()
            if not site_id:
                continue

            try:
                print(f"Processing site ID: {site_id}")
                talon_view.select_session_and_assign_username(site_id)
                talon_view.enter_initial_session()
                time.sleep(8)
                
                print(f"Entered the session for {site_id}")
                talon_view.display_folder_names()

                flight_list = ["bsm", "bso", "access road", "center in", "center out", "downlook", "uplook", "tower flights", "tower flight", "compound", "cable run", "center", "tower climb", "DL"]

                folder_elements = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".session-folders-item .session-folders-item-name"))
                )
                folder_names = [folder.text.lower() for folder in folder_elements]

                matches = []
                empty_folders = []
                for folder_name in folder_names:
                    has_flight = False
                    for flight in flight_list:
                        if flight in folder_name:
                            matches.append(folder_name)
                            has_flight = True
                            break
                    if not has_flight:
                        empty_folders.append(folder_name)

                if empty_folders:
                    print(f"Folders with no flights for {site_id}: {empty_folders}")

                if matches:
                    print(f"Matches found in folders for {site_id}:", matches)
                    for match in matches:
                        matching_folder_element = next((folder for folder in folder_elements if folder.text.lower() == match), None)

                        if matching_folder_element:
                            # Check if the 360° view already exists
                            if talon_view.is_360_present(match):
                                print(f"Skipping adding 360° view for '{match}' as it already exists.")
                                continue  # Skip to the next match

                            print(f"Adding {match} to {site_id}")
                            talon_view.click_add_button()
                            talon_view.click_360_view_button()
                            talon_view.click_add_folder_to_item_button(matching_folder_element.text.strip())
                            talon_view.click_done_button()
                
                # Search for the site in Matterport
                matterport_spider.search_site(site_id)
                share_link = matterport_spider.get_share_link()

                if share_link:
                    time.sleep(5)
                    talon_view.click_add_button()
                    talon_view.add_matterport()
                    talon_view.input_matterport_url()  # Call the new function here
                    talon_view.add_matterport_confirm()
                else:
                    print(f"No share link found for site ID {site_id}. Proceeding to pass/fail prompt.")
                    # Removed 'continue' to ensure it goes to the pass/fail prompt

                # Pause for user input
                pass_fail = input(f"Did the session for site ID {site_id} pass or fail? (pass/fail/skip): ").strip().lower()

                fail_reason = ""
                if pass_fail == "fail":
                    fail_reason = input("Please provide the reason for failure: ").strip()
                
                # Add the result to the list if it's not a skip
                if pass_fail != "skip":
                    results.append((site_id, pass_fail, driver.current_url, fail_reason))
                
                # Navigate back to the all sessions page
                driver.get("https://mechanicalvisionsolutions.collaborate.center/all-sessions")
                
                print(f"Finished processing site ID: {site_id}")
                print("results so far: ", results)
            except Exception as e:
                print(f"An error occurred while processing site ID {site_id}: {str(e)}")
                


            print("Ready for next site ID.")



    # Print the results
    for result in results:
        print(result)

    print("Exiting the program.")
    driver.quit()

if __name__ == "__main__":
    main()
