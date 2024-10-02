# main.py
from mpspider import *
from sfspider import *
from tvspiderforturnins import *
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from dotenv import load_dotenv
import os
from gui import SiteTableGUI
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QThread, pyqtSignal, QObject
import sys
import json

load_dotenv()

def load_progress():
    if os.path.exists('progress.json'):
        with open('progress.json', 'r') as f:
            results = json.load(f)
            # Convert each sublist to a tuple
            results = [tuple(item) for item in results]
    else:
        results = []
    # Convert results to a dictionary
    processed_sites_dict = {item[0]: item for item in results}
    return results, processed_sites_dict

def save_progress(results):
    with open('progress.json', 'w') as f:
        # Convert tuples to lists for JSON serialization
        json.dump([list(item) for item in results], f)

class SiteProcessor(QObject):
    # Signals
    progress = pyqtSignal(str)
    site_processed = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, talon_view, matterport_spider, site_turnins, results, processed_sites_dict):
        super().__init__()
        self.talon_view = talon_view
        self.matterport_spider = matterport_spider
        self.site_turnins = site_turnins
        self.results = results  # Loaded from progress.json
        self.processed_sites_dict = processed_sites_dict
        self.sites_data = []
        self.current_index = 0
        self.site_urls = {}

    def save_progress(self):
        with open('progress.json', 'w') as f:
            # Convert tuples back to lists for JSON serialization
            json.dump([list(item) for item in self.results], f)

    def process_sites(self, sites_data):
        self.sites_data = sites_data
        self.current_index = 0
        self.process_next_site()

    def process_next_site(self):
        if self.current_index < len(self.sites_data):
            site_data = self.sites_data[self.current_index]
            site_id = site_data['site_id']
            try:
                self.progress.emit(f"Processing site ID: {site_id}")
                # Perform the processing steps
                self.talon_view.select_session_and_assign_username(site_id)
                self.talon_view.enter_initial_session()
                time.sleep(8)
                self.progress.emit(f"Entered the session for {site_id}")
                self.talon_view.display_folder_names()
                # ... rest of the processing steps ...
                # For example:
                flight_list = ["bsm", "bso", "access road", "center in", "center out", "downlook", "uplook", "tower flights", "tower flight", "compound", "cable run", "center", "tower climb", "DL"]

                folder_elements = WebDriverWait(self.talon_view.driver, 10).until(
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
                    self.progress.emit(f"Folders with no flights for {site_id}: {empty_folders}")

                if matches:
                    self.progress.emit(f"Matches found in folders for {site_id}: {matches}")
                    for match in matches:
                        matching_folder_element = next((folder for folder in folder_elements if folder.text.lower() == match), None)

                        if matching_folder_element:
                            # Check if the 360° view already exists
                            if self.talon_view.is_360_present(match):
                                self.progress.emit(f"Skipping adding 360° view for '{match}'")
                                continue  # Skip to the next match

                            self.progress.emit(f"Adding {match} to {site_id}")
                            self.talon_view.click_add_button()
                            self.talon_view.click_360_view_button()
                            self.talon_view.click_add_folder_to_item_button(matching_folder_element.text.strip())
                            self.talon_view.click_done_button()
                # Check and count photos in "Downlook" or "DL" folder
                relevant_folders = ["downlook", "dl"]
                photo_counts = self.talon_view.count_photos_in_folder(relevant_folders)
                self.progress.emit(f"Photo counts for site ID {site_id}: {photo_counts}")

                # Search for the site in Matterport
                try:
                    self.matterport_spider.search_site(site_id)
                    # share_link = self.matterport_spider.get_share_link()
                except Exception as e:
                    self.progress.emit(f"Suppressed error while searching for site or getting share link: {e}")
                    # share_link = None

                # Store the current URL
                self.site_urls[site_id] = self.talon_view.driver.current_url

                # After processing, emit signal to indicate site processed
                self.progress.emit(f"Finished processing site ID: {site_id}")
                self.site_processed.emit(site_id)
            except Exception as e:
                self.progress.emit(f"An error occurred while processing site ID {site_id}: {str(e)}")
                # Proceed to collect user input for the site
                self.site_processed.emit(site_id)
        else:
            # All sites processed
            self.progress.emit("All sites have been processed.")
            self.finished.emit()

    def on_user_input_received(self, site_id, result, fail_reason):
        # Retrieve the URL for this site
        url = self.site_urls.get(site_id, "")
        # Store the result with the URL
        self.results.append((site_id, result.lower(), url, fail_reason))
        # Update processed_sites_dict
        self.processed_sites_dict[site_id] = (site_id, result.lower(), url, fail_reason)
        # Save progress
        self.save_progress()
        # Navigate back to the all sessions page
        self.talon_view.driver.get("https://mechanicalvisionsolutions.collaborate.center/all-sessions")
        # **Navigate Matterport to All Spaces**
        self.matterport_spider.return_to_models_page()
        self.current_index += 1
        # Process next site
        self.process_next_site()

def main():
    app = QApplication(sys.argv)

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

    ### New Steps Start Here ###
    # Open a new tab for Salesforce
    driver.execute_script("window.open('');")
    driver.switch_to.window(driver.window_handles[2])

    # Initialize Salesforce and SiteTurnins instances
    salesforce = Salesforce(driver)
    site_turnins = SiteTurnins(driver)

    # Log in to Salesforce and navigate to the "Ready for QA" page
    salesforce.login()
    salesforce.navigate_to_ready_for_qa()

    # click the status counter button twice
    salesforce.click_status_counter_button()

    # Parse the report table and store the data in a variable
    parsed_table_data = site_turnins.parse_report_table()

    # Load existing progress
    results, processed_sites_dict = load_progress()

    # Switch back to the main TalonView tab
    driver.switch_to.window(driver.window_handles[0])
    ### New Steps End Here ###

    # Launch the GUI
    gui = SiteTableGUI(parsed_table_data, processed_sites_dict)

    # Create the SiteProcessor object
    site_processor = SiteProcessor(talon_view, matterport_spider, site_turnins, results, processed_sites_dict)

    # Create a QThread object
    thread = QThread()

    # Move the SiteProcessor to the thread
    site_processor.moveToThread(thread)

    # Connect signals and slots
    gui.sites_processed.connect(site_processor.process_sites)
    site_processor.progress.connect(gui.update_progress)
    site_processor.finished.connect(thread.quit)
    site_processor.finished.connect(lambda: print("All sites processed."))

    site_processor.site_processed.connect(gui.on_site_processed)
    gui.user_input_received.connect(site_processor.on_user_input_received)

    # Start the thread when sites are processed
    gui.sites_processed.connect(thread.start)

    # Connect the new turn in signal
    def on_turn_in_sites():
        # Switch driver to Salesforce window
        driver.switch_to.window(driver.window_handles[2])
        # Combine results
        all_results = site_processor.results  # Should include loaded results and new ones
        # Pass all_results to open_inspection_tabs
        site_turnins.open_inspection_tabs(all_results)
        # After successful turn-in, remove processed sites from progress.json
        for site_id, _, _, _ in all_results:
            if site_id in processed_sites_dict:
                del processed_sites_dict[site_id]
        # Update results
        site_processor.results = list(processed_sites_dict.values())
        # Save the updated progress
        save_progress(site_processor.results)
        # Inform the user
        gui.update_progress("Turn-in completed. Progress file updated.")

    gui.turn_in_sites_signal.connect(on_turn_in_sites)

    gui.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()