from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys
import csv
import time
import traceback

wait_time = 2

# Add more locations if needed
locations = [
    "Perth",
]

# Create a new instance of the Chrome driver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
url = "https://www.tutorfinder.com.au/tutors/search.php"
driver.get(url)

last = False

dropdown_element = WebDriverWait(driver, wait_time).until(
    EC.presence_of_element_located((By.XPATH, '//*[@id="vSubjectID"]'))
)

select = Select(dropdown_element)

options_text = [option.text for option in select.options]

# Uncomment the line below for custom options
# options_text = ["Physics", ""]

# Data list to store the extracted information
data = []

for option_text in options_text[:-1]:  # Exclude the last option
    dropdown_element = WebDriverWait(driver, wait_time).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="vSubjectID"]'))
    )

    select = Select(dropdown_element)

    select.select_by_visible_text(option_text)

    for location in locations:
        enter_location_text = WebDriverWait(driver, wait_time).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="SidebarLocation"]'))
        )

        enter_location_text.clear()
        enter_location_text.send_keys(location)

        time.sleep(1)
        enter_location_text.send_keys(Keys.ENTER)
        enter_location_text.send_keys(Keys.ENTER)

        i = 1
        last = False
        while True:
            try: # try-except block to handle the case when the page number is not found
                page_num = WebDriverWait(driver, wait_time).until(
                    EC.presence_of_all_elements_located((By.CLASS_NAME, "page-link"))
                )

                for page in page_num:
                    if page.text == page_num[-1].text:
                        last = True
                    if page.text == str(i):
                        page.click()
                        break

                i += 1
            except:
                print("Page number not found")
                last = True

            try: # try-except block to handle the case when the table is not found
                table = WebDriverWait(driver, wait_time).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "tf-table"))
                )

                # Extract rows
                rows = table.find_elements(By.TAG_NAME, "tr")

                # Extract data
                j = 0
                for _ in range(len(rows)):  # Exclude the header row

                    table = WebDriverWait(driver, wait_time).until(
                        EC.presence_of_element_located((By.CLASS_NAME, "tf-table"))
                    )

                    # Extract rows
                    rows = table.find_elements(By.TAG_NAME, "tr")

                    cells = rows[j + 1].find_elements(By.TAG_NAME, "td")
                    temp_cells = [cell.text for cell in cells]

                    phone_number = "-"
                    email = "-"
                    experience = "-"
                    qualifications = "-"
                    rates = "-"
                    gender = "-"
                    registered = "-"
                    website = "-"

                    details = WebDriverWait(driver, wait_time).until(
                        EC.presence_of_all_elements_located((By.CLASS_NAME, "c_link"))
                    )
                    details[j].click()

                    contact_link = WebDriverWait(driver, wait_time).until(
                        EC.presence_of_element_located((By.XPATH, '//a[u[text()="Show Contact Details"]]'))
                    )
                    contact_link.click()

                    h3_elements = WebDriverWait(driver, wait_time).until(
                        EC.presence_of_all_elements_located(
                            (By.XPATH, "/html/body/div[1]/div[3]/div[2]/div/div[1]/div/h3")
                        )
                    )

                    try:
                        # Wait for all <span> elements with the class 'c_link' to be present
                        span_elements = WebDriverWait(driver, wait_time).until(
                            EC.presence_of_all_elements_located((By.CLASS_NAME, "c_link"))
                        )
                    except:
                        span_elements = []

                    # Loop through the <span> elements
                    for span in span_elements:

                        # Use JavaScript to find the nearest <svg> element
                        data_icon = driver.execute_script(
                            """
                                let span = arguments[0];
                                // Check if the previous sibling <b> contains the <svg> element
                                let sibling = span.previousElementSibling;
                                if (sibling && sibling.querySelector('svg')) {
                                    return sibling.querySelector('svg').getAttribute('data-icon');
                                }
                                else {
                                    return sibling && sibling.getAttribute('data-icon');
                                }
                            """,
                            span,
                        )

                        # Assign values based on the 'data-icon' attribute
                        if data_icon == "phone":
                            phone_number = span.text
                        elif data_icon == "wifi":
                            website = span.text
                        elif data_icon == "envelope":
                            email = span.text

                    for h3 in h3_elements:

                        next_sibling_text = driver.execute_script(
                            """
                                var h3 = arguments[0];
                                var sibling = h3.nextSibling;
                                while (sibling && sibling.nodeType !== 3) {  // Ensure it's a text node (nodeType 3)
                                    sibling = sibling.nextSibling;
                                }
                                return sibling ? sibling.textContent : null;
                            """,
                            h3,
                        )

                        if "Experience" in h3.text:
                            experience = next_sibling_text.strip()
                        elif "Qualifications" in h3.text:
                            qualifications = next_sibling_text.strip()
                        elif "Rates" in h3.text:
                            rates = next_sibling_text.strip()
                        elif "Gender" in h3.text:
                            gender = next_sibling_text.strip()
                        elif "Registered" in h3.text:
                            registered = next_sibling_text.strip()

                    back_button = WebDriverWait(driver, wait_time).until(
                        EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div[3]/div[2]/div/div[1]/nav/a"))
                    )
                    back_button.click()

                    j += 1

                    data.append(
                        {
                            "Tutor Name": temp_cells[0],
                            "State": location,
                            "Suburb": temp_cells[1],
                            "Subjects": option_text,
                            "Rate": temp_cells[2],
                            "Listing": temp_cells[3],
                            "Phone number": phone_number,
                            "Email": email,
                            "Experience": experience,
                            "Qualifications": qualifications,
                            "Rates": rates,
                            "Gender": gender,
                            "Registered": registered,
                            "Website": website,
                        }
                    )
                    
            except:
                print("End of table or table not found")
                # traceback.print_exc()

            if last:
                break

# Save data to CSV
with open("tutors.csv", "w", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=["Tutor Name", "State", "Suburb", "Subjects", "Rate", "Listing", "Phone number", "Email", "Experience", "Qualifications", "Rates", "Gender", "Registered", "Website"])
    writer.writeheader()  # Write column headers
    writer.writerows(data)  # Write data rows

print("Data saved to tutors.csv")

# Close the driver
driver.quit()
