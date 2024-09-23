from mpspider import *
from sfspider import *
from tvspiderforturnins import *
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

def main():
    # Initialize drivers and spiders
    driver = TalonViewAutomation.initialize_driver()

    # Load TalonView credentials from environment variables
    tv_username = os.getenv("TALONVIEW_USERNAME")
    tv_password = os.getenv("TALONVIEW_PASSWORD")
    talon_view = TalonViewAutomation(driver, tv_username, tv_password)
    talon_view.sign_in()

    # Load Matterport credentials from environment variables
    matterport_username = os.getenv("MATTERPORT_USERNAME")
    matterport_password = os.getenv("MATTERPORT_PASSWORD")
    matterport_spider = MatterportSpider(matterport_username, matterport_password)
    matterport_spider.login()

    while True:
        site_ids = input("Enter a list of site IDs separated by commas (or type 'exit' to quit): ").strip().split(',')

        if site_ids[0].lower() == 'exit':
            break

        results = []

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

                # Static flight list with possible variations
                flight_list = ["bsm, bso, access road", "center in", "center out", "downlook", "uplook", "tower flights", "tower flight", "compound", "cable run", "center"]

                # Check for matches in folder names
                folder_elements = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".session-folders-item .session-folders-item-name"))
                )
                folder_names = [folder.text.lower() for folder in folder_elements]
                
                matches = []
                for folder_name in folder_names:
                    for flight in flight_list:
                        if flight in folder_name:
                            matches.append(folder_name)
                            break  # Move to the next folder_name if a match is found

                if matches:
                    print(f"Matches found in folders for {site_id}:", matches)
                    for match in matches:
                        matching_folder_element = next((folder for folder in folder_elements if folder.text.lower() == match), None)

                        if matching_folder_element:
                            print(f"Adding {match} to {site_id}")
                            talon_view.click_add_button()
                            talon_view.click_360_view_button()
                            talon_view.click_add_folder_to_item_button(matching_folder_element.text.strip())
                            talon_view.click_done_button()

                    # Add Matterport after adding the last 360
                    print(f"Adding Matterport to {site_id}")
                    talon_view.click_add_button()
                    talon_view.add_matterport()

                    # Switch to a new tab for Matterport operations
                    driver.execute_script("window.open('');")
                    driver.switch_to.window(driver.window_handles[-1])

                    matterport_spider.search_site(site_id)
                    matterport_link = matterport_spider.get_share_link()

                    # Switch back to the TalonView tab
                    driver.switch_to.window(driver.window_handles[0])

                    # TODO: Add logic to determine pass/fail and get the TalonView link
                    # For now, we'll use placeholder values
                    result = "pass"  # or "fail"
                    talonview_link = driver.current_url
                    fail_reason = ""  # Add logic to get fail reason if applicable

                    results.append((site_id, result, talonview_link, fail_reason))

                # Navigate back to the all sessions page
                driver.get("https://mechanicalvisionsolutions.collaborate.center/all-sessions")
                
                print(f"Finished processing site ID: {site_id}")
                
            except Exception as e:
                print(f"An error occurred while processing site ID {site_id}: {str(e)}")
                results.append((site_id, "fail", "", str(e)))

            print("Ready for next site ID.")

        print("Results:")
        for result in results:
            print(result)

    print("Exiting the program.")
    driver.quit()

if __name__ == "__main__":
    main()

