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

load_dotenv()

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

    # Parse the report table and store the data in a variable
    parsed_table_data = site_turnins.parse_report_table()

    # Launch the GUI
    app = QApplication(sys.argv)
    gui = SiteTableGUI(parsed_table_data)
    gui.show()
    app.exec_()
    # Get the selected sites from the GUI
    selected_sites = gui.selected_sites

    # Switch back to the main TalonView tab
    driver.switch_to.window(driver.window_handles[0])
    ### New Steps End Here ###

    results = []

    while True:
        if not selected_sites:
            break

        site_ids = selected_sites
        selected_sites = []  # Clear the list after processing

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
                                print(f"Skipping adding 360° view for '{match}'")
                                continue  # Skip to the next match

                            print(f"Adding {match} to {site_id}")
                            talon_view.click_add_button()
                            talon_view.click_360_view_button()
                            talon_view.click_add_folder_to_item_button(matching_folder_element.text.strip())
                            talon_view.click_done_button()
            
                # Check and count photos in "Downlook" or "DL" folder
                relevant_folders = ["downlook", "dl"]
                photo_counts = talon_view.count_photos_in_folder(relevant_folders)
                print(f"Photo counts for site ID {site_id}: {photo_counts}")
            
            
                # Search for the site in Matterport
                try:
                    matterport_spider.search_site(site_id)
                    #share_link = matterport_spider.get_share_link()
                except Exception as e:
                    print(f"Suppressed error while searching for site or getting share link: {e}")
                    share_link = None

                # if share_link:
                #     time.sleep(5)
                #     talon_view.click_add_button()
                #     talon_view.add_matterport()
                #     talon_view.input_matterport_url()  # Call the new function here
                #     talon_view.add_matterport_confirm()

                #     # Return to the Matterport models page after processing the site
                #     matterport_spider.return_to_models_page()

                # else:
                #     print(f"No share link found for site ID {site_id}. Proceeding to pass/fail prompt.")
                #     # Removed 'continue' to ensure it goes to the pass/fail prompt

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
                
                try:
                    # Navigate back to the all sessions page
                    driver.get("https://mechanicalvisionsolutions.collaborate.center/all-sessions")
                except Exception as nav_e:
                    print(f"Failed to navigate back: {nav_e}")

                # Proceed to the pass/fail input step
                try:
                    pass_fail = input(f"Did the session for site ID {site_id} pass or fail? (pass/fail/skip): ").strip().lower()
                except Exception as input_e:
                    print(f"Failed to get pass/fail input: {input_e}")
                    pass_fail = "skip"

                fail_reason = ""
                if pass_fail == "fail":
                    try:
                        fail_reason = input("Please provide the reason for failure: ").strip()
                    except Exception as input_e:
                        print(f"Failed to get failure reason: {input_e}")
                        fail_reason = "No reason provided."

                # Add the result to the list if it's not a skip
                if pass_fail != "skip":
                    results.append((site_id, pass_fail, driver.current_url, fail_reason))
                
                print(f"Finished processing site ID: {site_id} with error handling.")
                print("results so far: ", results)
                
                continue  # Proceed to the next site_id

        # Ask the user if they want to turn in the sites after reviewing all site IDs
        turn_in_sites = input("Do you want to turn in the sites now? (yes/no): ").strip().lower()
        if turn_in_sites == 'yes':
            print("Turning in the sites...")

            # Initialize Salesforce and SiteTurnins classes
            # (Already initialized earlier; no need to re-initialize)

            # Pass the results to the SiteTurnins class to process the site turn-ins
            site_turnins.open_inspection_tabs(results)
        else:
            print("Skipping the turn-in process.")

        print("Ready for next site ID.")

    # Print the results
    for result in results:
        print(result)

    print("Exiting the program.")
    driver.quit()

    # Close the GUI after the program is completed


if __name__ == "__main__":
    main()


