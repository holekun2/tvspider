#selenium
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.common.exceptions import StaleElementReferenceException
from dotenv import load_dotenv
import os
from selenium.common.exceptions import NoSuchElementException
# Load environment variables from .env file
load_dotenv()

# Set up the WebDriver
driver = webdriver.Chrome()

# Open the website
class Salesforce:
    def __init__(self, driver):
        self.driver = driver
        # Load Salesforce credentials from environment variables
        self.sfusername = os.getenv("SALESFORCE_USERNAME")
        self.sfpassword = os.getenv("SALESFORCE_PASSWORD")

    def login(self):
        self.driver.get("https://talonaerolyticsinc.my.site.com/alliancemember/s/login/?ec=302&startURL=%2Falliancemember%2Fs%2F")
        time.sleep(5)

        username_field = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='Username']"))
        )
        username_field.clear()
        username_field.send_keys(self.sfusername)

        password_field = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='Password']"))
        )
        password_field.clear()
        password_field.send_keys(self.sfpassword)

        login_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[text()='Log in']"))
        )
        login_button.click()
        time.sleep(5)

    def navigate_to_ready_for_qa(self):
        # Navigate to the report page after logging in
        self.driver.get("https://talonaerolyticsinc.my.site.com/alliancemember/s/report/00OUT000001XYn72AG/ready-for-qa?queryScope=mru")

        # Wait for the report page to load
        time.sleep(5)


class SiteTurnins:
    def __init__(self, driver):
        self.driver = driver

    def open_inspection_tabs(self, site_data):
        for site_id, result, url, fail_reason in site_data:
            # Wait for the page to load
            time.sleep(5)

            # Switch to the iframe
            try:
                iframe = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "iframe.isView.reportsReportBuilder"))
                )
                self.driver.switch_to.frame(iframe)
            except Exception as e:
                print(f"Error finding iframe: {e}")
                continue  # Skip to the next site_id if iframe is not found

            # Define the site ID you want to look up
            siteIdToFind = site_id
            print(f"Looking for site ID: {siteIdToFind}")

            # Wait for the table rows to be present
            try:
                rows = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'tr.data-grid-table-row'))
                )
                print(f"Found {len(rows)} rows.")
            except Exception as e:
                print(f"Error finding rows: {e}")
                self.driver.switch_to.default_content()
                continue

            for row in rows:
                try:
                    site_id_cell = row.find_element(By.CSS_SELECTOR, 'td[data-column-index="2"]')
                    print(f"Checking row with site ID: {site_id_cell.text.strip()}")
                    if site_id_cell and site_id_cell.text.strip() == siteIdToFind:
                        # Get the link from the first column
                        inspection_link = row.find_element(By.CSS_SELECTOR, 'td[data-column-index="0"] a')
                        if inspection_link:
                            print(f"Found link: {inspection_link.get_attribute('href')}")
                            # Open the link in a new tab
                            self.driver.execute_script("window.open(arguments[0].href, '_blank');", inspection_link)
                        break  # Exit the loop once the site ID is found
                except NoSuchElementException:
                    # Silently continue to the next row if the element is not found
                    continue
                except Exception as e:
                    # Log other exceptions without printing the full error message
                    print(f"Unexpected error processing row: {type(e).__name__}")

            # Switch back to the main content
            self.driver.switch_to.default_content()

            # Switch to the new tab
            if len(self.driver.window_handles) > 1:
                self.driver.switch_to.window(self.driver.window_handles[-1])
            else:
                print("No new tab to switch to.")
                continue

            # Wait for the new tab to load
            print("Waiting for the new tab to load...")
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))

            # Click the "New" button
            print("Looking for the 'New' button...")
            new_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//a[@title='New' and @role='button']"))
            )
            print("Clicking the 'New' button...")
            new_button.click()

            # Wait for the new page to load
            time.sleep(3)

            # Click the "Reviewed by QA" input and select the option
            reviewed_by_qa_input = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "input[placeholder='Search People...']"))
            )

            # Find all input fields with the placeholder 'Search People...'
            input_fields = self.driver.find_elements(By.CSS_SELECTOR, "input[placeholder='Search People...']")

            # Check if there are at least two such elements
            if len(input_fields) >= 2:
                # Access the second input field
                input_field = input_fields[1]

                # Define the name to select as a variable
                name_to_select = 'John James'  # Change this to the desired name

                # Focus on the input field and enter the name
                input_field.click()
                input_field.clear()
                input_field.send_keys(name_to_select)

                # Wait for the autocomplete options to appear
                time.sleep(0.5)  # Adjust the sleep time as needed

                # Retry mechanism for handling stale elements
                for attempt in range(3):  # Retry up to 3 times
                    try:
                        # Construct XPath to find the div with the matching title
                        option_xpath = f"//a[@role='option']//div[@class='primaryLabel slds-truncate slds-lookup__result-text' and @title='{name_to_select}']"

                        # Wait until the matching option is clickable
                        matching_option = WebDriverWait(self.driver, 10).until(
                            EC.element_to_be_clickable((By.XPATH, option_xpath))
                        )

                        # Click the parent <a> element to select the option
                        matching_option.find_element(By.XPATH, "./ancestor::a").click()

                        print(f"Successfully selected '{name_to_select}'.")
                        break  # Exit the retry loop if successful
                    except StaleElementReferenceException:
                        print(f"Stale element encountered. Retrying... (Attempt {attempt + 1}/3)")
                        time.sleep(1)  # Wait a bit before retrying
                    except Exception as e:
                        print(f"Error: {e}")
                        break

            else:
                print("Second input field not found.")

            # Click the "Review Result" dropdown
            dropdowns = self.driver.find_elements(By.XPATH, "//a[@role='combobox' and contains(@aria-describedby, 'a-label')]")
            for dropdown in dropdowns:
                try:
                    # Check if the dropdown is within the desired container
                    container = dropdown.find_elements(By.XPATH, "ancestor::div[@data-target-selection-name='sfdc:RecordField.Quality_Reviews__c.Review_Result__c']")
                    if container:
                        dropdown.click()
                        time.sleep(3)

                        # Select "QA Pass" or "QA Fail" based on the site ID
                        if result.lower() == "pass":
                            qa_pass_option = WebDriverWait(self.driver, 10).until(
                                EC.element_to_be_clickable((By.XPATH, "//li[contains(@class, 'uiMenuItem') and contains(@class, 'uiRadioMenuItem')]//a[@title='QA Pass']"))
                            )
                            qa_pass_option.click()

                            # Enter the URL into the URL input
                            url_input = WebDriverWait(self.driver, 10).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='url']"))
                            )
                            url_input.clear()
                            url_input.send_keys(url)

                        elif result.lower() == "fail":
                            qa_fail_option = WebDriverWait(self.driver, 10).until(
                                EC.element_to_be_clickable((By.XPATH, "//li[contains(@class, 'uiMenuItem') and contains(@class, 'uiRadioMenuItem')]//a[@title='QA Fail']"))
                            )
                            qa_fail_option.click()

                            # Enter the URL into the URL input
                            url_input = WebDriverWait(self.driver, 10).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='url']"))
                            )
                            url_input.clear()
                            url_input.send_keys(url)

                            # Enter the fail reason into the fail info input
                            fail_info_input = WebDriverWait(self.driver, 10).until(
                                EC.presence_of_element_located((By.CSS_SELECTOR, "textarea"))
                            )
                            fail_info_input.clear()
                            fail_info_input.send_keys(fail_reason)
                        else:
                            print(f"Please select a result for site ID: {site_id}")
                        break  # Exit the loop once the correct dropdown is processed
                except Exception as e:
                    # Suppress the error message
                    pass

            time.sleep(3)

            # Click the "Cancel" button
            cancel_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//span[text()='Cancel']"))
            )
            cancel_button.click()
            time.sleep(3)

            # Close the tab and switch back to the original window
            self.driver.close()
            self.driver.switch_to.window(self.driver.window_handles[0])

    def parse_report_table(self):
        """
        Parses the entire table on the report page and returns it as a list of lists.
        
        Returns:
            list: A list of lists representing the table data.
        """
        table_data = []
        try:
            # Switch to the iframe containing the table using the provided CSS selector
            iframe_css_selector = "iframe.isView.reportsReportBuilder"
            iframe = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, iframe_css_selector))
            )
            self.driver.switch_to.frame(iframe)
            print("Switched to the report iframe.")

            # Wait for a short duration to ensure the table is fully loaded
            time.sleep(2)

            # Use the same CSS selector for the table as in open_inspection_tabs
            table_css_selector = 'tr.data-grid-table-row'

            try:
                rows = WebDriverWait(self.driver, 20).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, table_css_selector))
                )
                print("Report table rows found using the provided CSS selector.")
            except Exception as e:
                print(f"Failed to locate table rows using CSS selector. Error: {e}")
                return table_data

            # Extract table headers (if needed, optional)
            headers = []
            header_elements = self.driver.find_elements(By.CSS_SELECTOR, "thead th")
            if not header_elements:
                print("No header elements found. The table might be empty or headers use different tags.")
            for header in header_elements:
                headers.append(header.text.strip())
            if headers:
                print(f"Table headers: {headers}")
            else:
                print("No headers extracted.")

            # Extract table rows
            for row in rows:
                row_data = []
                cells = row.find_elements(By.CSS_SELECTOR, "td")
                if not cells:
                    print("No cells found in this row. Skipping.")
                    continue
                for cell in cells:
                    cell_text = cell.text.strip()
                    row_data.append(cell_text)
                table_data.append(row_data)
            print(f"Extracted {len(table_data)} rows from the table.")

        except Exception as e:
            print(f"An error occurred while parsing the report table: {e}")
        finally:
            # Switch back to the default content
            self.driver.switch_to.default_content()
            print("Switched back to the default content.")
        
        return table_data

def main():
    # Initialize the classes
    salesforce   = Salesforce(driver)
    site_turnins = SiteTurnins(driver)

    # Navigate to the Ready for QA page
    salesforce.login()
    salesforce.navigate_to_ready_for_qa()
    
    # Parse the report table and store the data in a variable
    parsed_table_data = site_turnins.parse_report_table()
    
    # Wrap the prompting and processing in a loop
    while True:
        # Prompt the user to enter site data as a Python list of tuples
        site_data_input = input("Enter site data as a Python list of tuples (e.g., [('site_id', 'result', 'url', 'fail_reason')]): ")
        
        try:
            # Evaluate the input as a Python expression (list of tuples)
            site_data = eval(site_data_input)
            if not isinstance(site_data, list) or not all(isinstance(item, tuple) and len(item) == 4 for item in site_data):
                raise ValueError("Invalid format. Please enter a list of 4-element tuples.")
        except Exception as e:
            print(f"Error: {e}")
            continue

        site_turnins.open_inspection_tabs(site_data)

        # Ask if the user wants to process another set of sites
        another_set = input("Process another set of sites? (y/n): ")
        if another_set.lower() != 'y':
            break

    #press enter to continue
    input("Press Enter to continue...")

if __name__ == "__main__":
    main()
