#mpspider.py
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import time
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

class MatterportSpider:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.driver = self.initialize_driver()

    def initialize_driver(self):
        chrome_options = webdriver.ChromeOptions()
        # Disable Chrome's pop-up asking for permissions
        chrome_options.add_experimental_option("prefs", {
            "profile.default_content_setting_values.clipboard": 1,  # Auto-allow clipboard access
            "profile.default_content_setting_values.notifications": 1,  # Auto-allow notifications
            "profile.default_content_setting_values.geolocation": 1  # Auto-allow geolocation if needed
        })
        driver = webdriver.Chrome(options=chrome_options)
        return driver

    def login(self):
        self.driver.get("https://authn.matterport.com/login?target=https%3A%2F%2Fmy.matterport.com%2Fmodels")
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "email"))).send_keys(self.username)
        # Updated to use data-testid for password field
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "[data-testid='textfield_password']"))).send_keys(self.password)
        WebDriverWait(self.driver, 10).until(EC.element_to_be_clickable((By.ID, "submitBtn"))).click()

    def search_site(self, site_name):
        try:
            # Wait for the search bar to be present
            search_bar = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input.H_pqOjjyLod793oGrhYZ"))
            )
            # Clear the search bar if needed
            search_bar.clear()
            # Enter the site name into the search bar
            search_bar.send_keys(site_name)
            search_bar.send_keys(Keys.RETURN)

            # Wait for either the "No results" element or the first search result
            WebDriverWait(self.driver, 10).until(
                lambda driver: driver.find_elements(By.CSS_SELECTOR, "div[data-testid='listing-items-zero-results-placeholder']") or
                               driver.find_elements(By.XPATH, "//a[contains(@href, '/models/') and @class='vfpvhnncPUsGE6tooEIK']")
            )

            # Check if the "No results" element is present
            no_results_elements = self.driver.find_elements(By.CSS_SELECTOR, "div[data-testid='listing-items-zero-results-placeholder']")
            if no_results_elements:
                print(f"No results found for {site_name}.")
                return None  # Return None if no results are found

            # Otherwise, proceed with the first search result
            first_result = self.driver.find_element(By.XPATH, "//a[contains(@href, '/models/') and @class='vfpvhnncPUsGE6tooEIK']")
            print(f"Search result found for {site_name}: {first_result}")
            first_result.click()
            search_bar.clear()
            
        except Exception as e:
            
            return None  # Return None in case of an error

    def get_share_link(self):
        try:
            # Re-locate the share button before clicking
            share_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-testid='model-share-button']"))
            )
            share_button.click()

            # Re-locate the radio button before clicking
            radio_button = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[data-testid='radio'][value='unlisted']"))
            )
            radio_button.click()

            # Re-locate the copy button before clicking
            self.driver.execute_script("""
                document.querySelector('button.button-module_button__Z331g[data-testid="clipboard_copy"]').click();
            """)

            # Re-locate the close dialog button before clicking
            close_dialog_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-testid='dialog_close_button']"))
            )
            close_dialog_button.click()

            # Reopen the share popup and re-locate the share button
            share_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-testid='model-share-button']"))
            )
            share_button.click()

            # Get the copied link from the clipboard
            link = self.driver.execute_script("return navigator.clipboard.readText()")

            return link

        except Exception as e:
        
            return None  # Return None in case of an error

    def return_to_models_page(self):
        """
        Navigate back to the Matterport models page after processing a site.
        """
        try:
            print("Returning to Matterport models page...")
            self.driver.get("https://my.matterport.com/models")
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, "input.H_pqOjjyLod793oGrhYZ")))
            print("Returned to Matterport models page.")
        except Exception as e:
            print(f"An error occurred while returning to the models page: {e}")

    def main(self):
        self.login()
        site_id = input("enter site id to search for:")
        self.search_site(site_id)
        self.get_share_link()
        print(f"searching for site: {site_id}")
        input("Press Enter to continue...")

if __name__ == "__main__":
    # Load Matterport credentials from environment variables
    matterport_username = os.getenv("MATTERPORT_USERNAME")
    matterport_password = os.getenv("MATTERPORT_PASSWORD")
    
    spider = MatterportSpider(matterport_username, matterport_password)
    spider.main()
