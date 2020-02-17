from selenium import webdriver
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementNotInteractableException
from selenium.common.exceptions import ElementNotVisibleException
from selenium.webdriver.common.action_chains import ActionChains
from datetime import datetime

from notification import send

import time
import os
import logging
import sys

# Change this to main directory of which the program is run
path = "/Users/athorn/Desktop/IB/IPO-Doc-Web-Scraper"
website_url = "https://www.hkexnews.hk/index.htm"
chromedrive_dir = path + "/venv/chromedriver"

error = False  # global variable used to check if something fails while fetching docs

# -----------------------------------------------------------------------------------------------------
# Function - Create folder to store Listing Documents
# -----------------------------------------------------------------------------------------------------

def get_dir(dir_name):
    # detect the current working directory and print it
    # path = os.getcwd()
    logging.info("The working directory set is %s" % path)
    print("[INFO] The working directory set is %s" % path)

    new_dir = path + "/listing-documents/" + dir_name
    if not os.path.isdir(new_dir):
        try:
            os.mkdir(new_dir)
        except OSError:
            logging.error("Creation of the directory %s failed" % new_dir)
            print("[ERROR] Creation of the directory %s failed" % new_dir)
        else:
            logging.info("Successfully created the directory %s " % new_dir)
            print("[INFO] Successfully created the directory %s " % new_dir)
    else:
        logging.warning("The directory already exists %s " % new_dir)
        print("[WARNING] The directory already exists %s " % new_dir)
    return new_dir

# Function to actually take the screenshot
def takeScreenshot(screenshot_name, driver):
    # Take a screenshot of the website - the file will be attached to the email
    if driver.save_screenshot(screenshot_name):
        logging.info("Screenshot Successfully Taken")
        print("[INFO] Screenshot Successfully Taken")
    else:
        logging.error("Unable to Take Screenshot - No File Created")
        print("[ERROR] Unable to Take Screenshot - No File Created")


# Pressing the search button
def searchButton(driver):
    global error
    try:
        driver.find_element_by_css_selector('.filter__btn-applyFilters-js').click()
        logging.info("Applied filters")
        print("[INFO] Applied filters")
    except NoSuchElementException:
        logging.error("Could not apply filters")
        print("[ERROR] Could not apply filters")
        error = True


# Selecting the headline category from the dropdown list
def selectHeadlineCategory(driver):
    global error
    try:
        driver.find_element_by_css_selector('#tier1-select > div').click()

        textInBox = (
            driver.find_element_by_css_selector('#tier1-select ~ div > div > div > div > div > div ~ div').text)

        if textInBox != "Headline Category":
            logging.debug("Menu Selected: " + textInBox)
            print("[DEBUG] Menu Selected: " + textInBox)
            raise NoSuchElementException

        driver.find_element_by_css_selector('#tier1-select ~ div > div > div > div > div > div ~ div').click()

        logging.info("Headline Category: Successfully Selected")
        print("[INFO] Headline Category: Successfully Selected")

    except NoSuchElementException:
        logging.error("Headline Category - Selector Not Found")
        print("[ERROR] 'Headline Category' - Selector Not Found")
        error = True

    except ElementNotVisibleException:
        logging.error("Headline Category - Selector Not Found")
        print("[ERROR] 'Headline Category' - Selector Not Found")
        error = True


# Function to send the email containing fetched documents
def sendIPOEmail(ipoData, download_dir, docsSearchedFor):
    global error
    ipo_count = 0

    # Writing and sending the email
    if error is True:
        email_template = "error"
    else:
        # Count the number of IPO found based on the number of dictionary keys
        for r in ipoData:
            # if r is not empty
            if r:
                ipo_count = ipo_count + 1

        # logging.info("Number of IPO found: " + str(ipo_count))
        # print("[INFO] Number of IPO found: " + str(ipo_count))

        if ipo_count == 0:
            logging.warning("No New IPO Document(s) Found - No Data Retrieved")
            print('[WARNING] No New IPO Document(s) Found - No Data Retrieved')
            email_template = "no-ipo"
        else:
            email_template = "one-ipo"
            logging.info("Writing data into txt file...")
            print("[INFO] Writing data into txt file...")
            f = open("message.txt", "w+")
            f.write("Dear ${PERSON_NAME},\r\n")
            f.write("Here are the details of the IPO Document(s) found on HKEXnews website:\r\n")
            for key in ipoData:
                # print(key)
                for y in ipoData[key]:
                    f.write("%s : %s\n" % (y, ipoData[key][y]))
                if ipo_count > 1:
                    f.write("-----------------------------------\n")
            f.write("\n\nDocuments searched for: " + docsSearchedFor)
            # f.write("\n\nDocuments searched for: \n   Supplementary Listing Documents \n   Allotment Results \n   "
            #         "Supplemental Information Regarding IPOs \n   IPO Cancellations (Global Offering not to proceed)")
            f.close()

    # Sleep to ensure all data is written to file before sending
    time.sleep(5)

    send(template=email_template, number_ipo=ipo_count, working_dir=path, attachment_dir=download_dir)


# Initialize webdriver instance
def openDriver(download_dir):
    options = webdriver.ChromeOptions()
    profile = {"plugins.plugins_list": [{"enabled": False, "name": "Chrome PDF Viewer"}],  # Disable Chrome's PDF Viewer
               "download.default_directory": download_dir, "download.extensions_to_open": "applications/pdf"}
    options.add_experimental_option("prefs", profile)

    driver = webdriver.Chrome(options=options, executable_path=chromedrive_dir)

    # Open browser window at URL
    driver.maximize_window()
    driver.get(website_url)
    logging.info("Opened %s" % website_url)
    print("[INFO] Opened %s" % website_url)

    return driver


# Select Announcements and Notices from dropdown list - For some reason you can't select from a dropdown list within a
# dropdown list within a dropdown list, so instead it does a less filtered search and have to scan through more docs
def selectAnnouncementsAndNotices(driver):
    global error

    try:
        # Select dropdown list
        driver.find_element_by_css_selector('#rbAfter2006 > div > div > div').click()
        # Select Announcements and Notices
        driver.find_element_by_css_selector('#rbAfter2006 > div ~ div > div > div > div > ul > li ~ li ').click()

        textInBox = (
            driver.find_element_by_css_selector('#rbAfter2006 > div ~ div > div > div > div > ul > li ~ li > a').text)

        # print(textInBox)
        if textInBox != "Announcements and Notices":
            print("[DEBUG] Menu Selected: " + textInBox)
            raise NoSuchElementException

        driver.find_element_by_css_selector('#rbAfter2006 > div ~ div > div > div > div > ul > li ~ li > a '
                                            '~ div > div > ul > li').click()

        logging.info("Announcements and Notices: Successfully Selected")
        print("[INFO] Announcements and Notices: Successfully Selected")
    except (NoSuchElementException, ElementNotInteractableException):
        logging.error("Announcements and Notices - Selector Not Found")
        print("[ERROR] 'Announcements and Notices' - Selector Not Found")
        error = True

    except ElementNotVisibleException:
        logging.error("Announcements and Notices - Selector Not Found")
        print("[ERROR] 'Announcements and Notices' - Selector Not Found")
        error = True

    # time.sleep(1)


def loadMoreButton(date_today, driver):

    global error

    rows = driver.find_elements_by_css_selector('#titleSearchResultPanel > div > div > div ~ div ~ div > div ~ div > '
                                                'table > tbody tr')

    # If there are rows in the table, attempt to click load more button
    # If there aren't, don't look for load more button (it doesnt exist)
    if len(rows) != 0:

        # Fetch last row's date
        date = rows[-1].find_elements_by_tag_name("td")[0].text
        date = date[:10]

        # Bool to check if the load more button is present
        isPresent = len(driver.find_elements_by_css_selector('#recordCountPanel2 > '
                                                             'div.search-results__content-loadmore.component'
                                                             '-loadmore.component-loadmore-no-options > div > '
                                                             'div.component-loadmore__dropdown-container > ul > '
                                                             'li > a')) > 0

        # While Load More button is present, and last date == today's date
        while isPresent == True and date == date_today:
            # Need to show more
            try:
                # Scroll down page so that load more button can be clicked
                element = driver.find_element_by_css_selector(
                    '#recordCountPanel2 > div.search-results__content-loadmore.component-loadmore.component'
                    '-loadmore-no-options > div > div.component-loadmore__dropdown-container > ul > li > a')
                actions = ActionChains(driver)
                actions.move_to_element(element).perform()

                element.click()
            except (NoSuchElementException, ElementNotVisibleException):
                error = True
                logging.error("Load More - Button Not Found")
                print("[ERROR] 'Load More' - Button Not Found")

            logging.info("Load More Button Successfully Pressed")
            print("[INFO] Load More Button Successfully Pressed")

            time.sleep(5)

            # Check if Load More Button needs pressing again
            rows = driver.find_elements_by_css_selector(
                '#titleSearchResultPanel > div > div > div ~ div ~ div > div ~ div > '
                'table > tbody tr')

            date = rows[-1].find_elements_by_tag_name("td")[0].text
            date = date[:10]

            # Check if load more button is present
            isPresent = len(driver.find_elements_by_css_selector('#recordCountPanel2 > '
                                                                 'div.search-results__content-loadmore.component'
                                                                 '-loadmore.component-loadmore-no-options > div > '
                                                                 'div.component-loadmore__dropdown-container > ul > '
                                                                 'li > a')) > 0

# Get allotment results
def getAllotmentResults(driver, date_today, download_dir):

    time.sleep(1)
    ipo_count = 0
    count = 2

    # Finding IPOS

    loadMoreButton(date_today, driver)

    # Array used to store fetched IPO data
    ipoData = {}

    rows = driver.find_elements_by_css_selector('#titleSearchResultPanel > div > div > div ~ div ~ div > div ~ div > '
                                                'table > tbody tr')

    if len(rows) != 0:
        logging.info("Searching for Allotment Results...")
        print("[INFO] Searching for Allotment Results...")
        for row in rows:

            # Fetch data from each row and store into appropriately named variables
            date = row.find_elements_by_tag_name("td")[0].text

            dateOfStock = date[:10]
            # print(dateOfStock, stockcode, stockname, doctype.lower, url)

            # If stock on this row's date matches today's date
            # Store stock details into ipoData dictionary

            # Keyword search

            if dateOfStock == date_today:

                # doctype variable is populated with the HEADLINE not text of URL
                # This is because most / all docs released under "Allotment Results" headline are ones we want
                doctype = row.find_element_by_css_selector('td ~ td ~ td ~ td > div').text

                if "allotment" in doctype.lower() and "results" in doctype.lower():

                    stockcode = row.find_elements_by_tag_name("td")[1].text
                    stockname = row.find_elements_by_tag_name("td")[2].text
                    url = row.find_element_by_css_selector('td ~ td ~ td ~ td > span ~ div ~ div > a').get_attribute(
                        'href')

                    doctype = "allotment results"
                    # print(date, stockcode, doctype, url)
                    if stockcode in ipoData.keys():
                        ipoData[stockcode].update({'ALLOTMENT_RESULTS_URL_' + str(count): url, 'DATE': dateOfStock})
                        count = count + 1
                    else:
                        ipoData[stockcode] = {'DATE': dateOfStock, 'STOCK_CODE': stockcode, 'STOCK_NAME': stockname,
                                              'ALLOTMENT_RESULTS_URL': url}
        # print(ipoData)

        date = rows[0].find_elements_by_tag_name("td")[0].text
        dateOfStock = date[:10]
        logging.info("Last document found was published on " + dateOfStock)
        print("[INFO] Last document found was published on " + dateOfStock)
    else:
        logging.info("Announcements and Notices table is empty - No matches found")
        print("[INFO] Announcements and Notices table is empty - No matches found")

    # Screenshot not relevant most the time, too many results
    # # Take a screenshot of the website - the file will be attached to the email
    # screenshot_name = makeScreenshotString("AllotmentResults", download_dir)
    # takeScreenshot(screenshot_name, driver)

    for r in ipoData:
        # if r is not empty
        if r:
            ipo_count = ipo_count + 1

    logging.info("Number of Matches found: " + str(ipo_count))
    print("[INFO] Number of Matches found: " + str(ipo_count))

    return ipoData

# Get cancelled IPO documents
def getCancellationIPO(driver, date_today, download_dir):

    time.sleep(1)
    ipo_count = 0

    # Finding IPOS

    loadMoreButton(date_today, driver)

    # Array used to store fetched IPO data
    ipoData = {}

    rows = driver.find_elements_by_css_selector('#titleSearchResultPanel > div > div > div ~ div ~ div > div ~ div > '
                                                'table > tbody tr')

    if len(rows) != 0:
        logging.info("Searching for IPO Cancellations...")
        print("[INFO] Searching for IPO Cancellations...")
        for row in rows:

            # Fetch data from each row and store into appropriately named variables
            date = row.find_elements_by_tag_name("td")[0].text

            dateOfStock = date[:10]
            # print(dateOfStock, stockcode, stockname, doctype.lower, url)

            # If stock on this row's date matches today's date
            # Store stock details into ipoData dictionary

            # Keyword search
            if dateOfStock == date_today:

                # doctype variable is populated with text of URL hyperlink
                # This is because not every document published under the "Miscellaneous" headline is one we want
                # Need to scan specific URL hyperlink texts to see if it says any of the keywords
                doctype = row.find_element_by_css_selector('td ~ td ~ td ~ td > div ~ div > a').text

                if "global" in doctype.lower() and "offering" in doctype.lower() and "not" in doctype.lower() and "proceed" in doctype.lower():

                    # Only fetch the stockcode / stockname / url if the document passes through the filters
                    # This saves computer power
                    stockcode = row.find_elements_by_tag_name("td")[1].text
                    stockname = row.find_elements_by_tag_name("td")[2].text
                    url = row.find_element_by_css_selector('td ~ td ~ td ~ td > span ~ div ~ div > a').get_attribute(
                        'href')

                    doctype = "global offering not to proceed"
                    # print(date, stockcode, doctype, url)
                    if stockcode in ipoData.keys():
                        ipoData[stockcode].update({'GLOBAL_OFFERING_NOT_TO_PROCEED_URL': url, 'DATE': dateOfStock})
                    else:
                        ipoData[stockcode] = {'DATE': dateOfStock, 'STOCK_CODE': stockcode, 'STOCK_NAME': stockname,
                                              'GLOBAL_OFFERING_NOT_TO_PROCEED_URL': url}

                if "postponement" in doctype.lower() and "share" in doctype.lower() and "offer" in doctype.lower():

                    stockcode = row.find_elements_by_tag_name("td")[1].text
                    stockname = row.find_elements_by_tag_name("td")[2].text
                    url = row.find_element_by_css_selector('td ~ td ~ td ~ td > span ~ div ~ div > a').get_attribute(
                        'href')

                    doctype = "postponement of the share offer"
                    # print(date, stockcode, doctype, url)
                    if stockcode in ipoData.keys():
                        ipoData[stockcode].update({'POSTPONEMENT_OF_THE_SHARE_OFFER_URL': url, 'DATE': dateOfStock})
                    else:
                        ipoData[stockcode] = {'DATE': dateOfStock, 'STOCK_CODE': stockcode, 'STOCK_NAME': stockname,
                                              'POSTPONEMENT_OF_THE_SHARE_OFFER_URL': url}
        # print(ipoData)

        date = rows[0].find_elements_by_tag_name("td")[0].text
        dateOfStock = date[:10]
        logging.info("Last document found was published on " + dateOfStock)
        print("[INFO] Last document found was published on " + dateOfStock)
    else:
        logging.info("Announcements and Notices table is empty - No matches found")
        print("[INFO] Announcements and Notices table is empty - No matches found")

    # Screenshot not really relevant - too many results
    # # Take a screenshot of the website - the file will be attached to the email
    # screenshot_name = makeScreenshotString("IPOCancellations", download_dir)
    # takeScreenshot(screenshot_name, driver)

    for r in ipoData:
        # if r is not empty
        if r:
            ipo_count = ipo_count + 1

    logging.info("Number of IPO found: " + str(ipo_count))
    print("[INFO] Number of IPO found: " + str(ipo_count))

    return ipoData

# Get Supplemental Information Regarding IPO documents
def getSuppInfoRegardingIPO(driver, date_today, download_dir):

    time.sleep(1)
    ipo_count = 0
    count = 2

    # Finding IPOS

    loadMoreButton(date_today, driver)

    # Array used to store fetched IPO data
    ipoData = {}

    rows = driver.find_elements_by_css_selector('#titleSearchResultPanel > div > div > div ~ div ~ div > div ~ div > '
                                                'table > tbody tr')

    if len(rows) != 0:
        logging.info("Searching for Supplemental Information Regarding IPO...")
        print("[INFO] Searching for Supplemental Information Regarding IPO...")
        for row in rows:

            # Fetch data from each row and store into appropriately named variables
            date = row.find_elements_by_tag_name("td")[0].text

            dateOfStock = date[:10]
            # print(dateOfStock, stockcode, stockname, doctype.lower, url)

            # If stock on this row's date matches today's date
            # Store stock details into ipoData dictionary

            # Keyword search
            if dateOfStock == date_today:

                # doctype variable is populated with the HEADLINE not text of URL
                # This is because most / all docs released under
                # "Supplemental Info Regarding IPO" headline are ones we want
                doctype = row.find_element_by_css_selector('td ~ td ~ td ~ td > div').text

                if "supplemental" in doctype.lower() and "information" in doctype.lower() and "ipo" in doctype.lower():

                    stockcode = row.find_elements_by_tag_name("td")[1].text
                    stockname = row.find_elements_by_tag_name("td")[2].text
                    url = row.find_element_by_css_selector('td ~ td ~ td ~ td > span ~ div ~ div > a').get_attribute(
                        'href')

                    doctype = "supplemental info regarding IPO"
                    # print(date, stockcode, doctype, url)
                    if stockcode in ipoData.keys():
                        ipoData[stockcode].update({'SUPPLEMENTAL_INFO_REGARDING_IPO_URL_' + str(count): url, 'DATE': dateOfStock})
                        count = count + 1
                    else:
                        ipoData[stockcode] = {'DATE': dateOfStock, 'STOCK_CODE': stockcode, 'STOCK_NAME': stockname,
                                              'SUPPLEMENTAL_INFO_REGARDING_IPO_URL': url}
        # print(ipoData)

        date = rows[0].find_elements_by_tag_name("td")[0].text
        dateOfStock = date[:10]
        logging.info("Last document found was published on " + dateOfStock)
        print("[INFO] Last document found was published on " + dateOfStock)
    else:
        logging.info("Announcements and Notices table is empty - No matches found")
        print("[INFO] Announcements and Notices table is empty - No matches found")

    # Screenshot not really relevant, too many results
    # # Take a screenshot of the website - the file will be attached to the email
    # screenshot_name = makeScreenshotString("SupplementalInfoRegardingIPO", download_dir)
    # takeScreenshot(screenshot_name, driver)

    for r in ipoData:
        # if r is not empty
        if r:
            ipo_count = ipo_count + 1

    logging.info("Number of Matches found: " + str(ipo_count))
    print("[INFO] Number of Matches found: " + str(ipo_count))

    return ipoData

# Function to select Listing Documents -> Supplementary Listing Document
def selectSuppListingDocument(driver):
    global error

    try:

        # Select Listing documents
        driver.find_element_by_css_selector('#rbAfter2006 > div > div > div').click()
        driver.find_element_by_css_selector(
            '#rbAfter2006 > div ~ div > div > div > div > ul > li ~ li ~ li ~ li').click()

        # Scroll to Supplementary Listing Documents
        element = driver.find_element_by_css_selector('#rbAfter2006 > div ~ div > div > div > div > ul > li ~ li ~ '
                                                      'li ~ li > a ~ div > div > ul > li ~ li ~ li ~ li ~ li ~ li '
                                                      '~ li ~ li ~ li ~ li ~ li ~ li ~ li')
        actions = ActionChains(driver)
        actions.move_to_element(element).perform()

        textInBox = (driver.find_element_by_css_selector('#rbAfter2006 > div ~ div > div > div > div > ul > li ~ li ~ '
                                                         'li ~ li > a ~ div > div > ul > li ~ li ~ li ~ li ~ li ~ li '
                                                         '~ li ~ li ~ li ~ li ~ li ~ li ~ li').text)

        # print(textInBox)
        # Validation to check Supplementary Listing Document is selected
        if textInBox != "Supplementary Listing Document":
            print("[DEBUG] Menu Selected: " + textInBox)
            raise NoSuchElementException

        driver.find_element_by_css_selector('#rbAfter2006 > div ~ div > div > div > div > ul > li ~ li ~ '
                                            'li ~ li > a ~ div > div > ul > li ~ li ~ li ~ li ~ li ~ li '
                                            '~ li ~ li ~ li ~ li ~ li ~ li ~ li').click()

        logging.info("Supplementary Listing Document: Successfully Selected")
        print("[INFO] Supplementary Listing Document: Successfully Selected")
    except (NoSuchElementException, ElementNotInteractableException):
        logging.error("Supplementary Listing Document - Selector Not Found")
        print("[ERROR] 'Supplementary Listing Document' - Selector Not Found")
        error = True

    except ElementNotVisibleException:
        logging.error("Supplementary Listing Document - Selector Not Found")
        print("[ERROR] 'Supplementary Listing Document' - Selector Not Found")
        error = True

    # time.sleep(1)

# Get Supplementary Listing Documents
def getSuppListingDocument(driver, date_today, download_dir):

    ipo_count = 0
    time.sleep(1)

    # Finding IPOS

    loadMoreButton(date_today, driver)

    # Find the table in HTML
    # IF THEY CHANGE TABLE HTML, NEED TO FIND CSS SELECTOR AGAIN
    rows = driver.find_elements_by_css_selector('#titleSearchResultPanel > div > div > div ~ div ~ div > div ~ div > '
                                                'table > tbody tr')

    # Array used to store fetched IPO data
    ipoData = {}

    if len(rows) != 0:
        logging.info("Searching for Supplementary Listing Documents...")
        print("[INFO] Searching for Supplementary Listing Documents...")
        for row in rows:

            # Fetch data from each row and store into appropriately named variables
            date = row.find_elements_by_tag_name("td")[0].text

            dateOfStock = date[:10]
            # print(dateOfStock, stockcode, stockname, doctype.lower, url)

            # If stock on this row's date matches today's date
            # Store stock details into ipoData dictionary

            # Keyword search
            if dateOfStock == date_today:

                # doctype variable is populated with text of URL hyperlink
                doctype = row.find_element_by_css_selector('td ~ td ~ td ~ td > div ~ div > a').text

                if ("prospectus" in doctype.lower() and "supplemental" in doctype.lower()) or (
                        "prospectus" in doctype.lower() and "addendum" in doctype.lower()):

                    stockcode = row.find_elements_by_tag_name("td")[1].text
                    stockname = row.find_elements_by_tag_name("td")[2].text
                    url = row.find_element_by_css_selector('td ~ td ~ td ~ td > span ~ div ~ div > a').get_attribute(
                        'href')

                    if "prospectus" in doctype.lower() and "supplemental" in doctype.lower():
                        # Re-set the doctype to prevent this stock getting filtered again in a further if statement
                        doctype = "supplemental prospectus"
                        # print(date, stockcode, doctype, url)
                        if stockcode in ipoData.keys():
                            ipoData[stockcode].update({'SUPPLEMENTAL_PROSPECTUS_URL': url, 'DATE': dateOfStock})
                        else:
                            ipoData[stockcode] = {'DATE': dateOfStock, 'STOCK_CODE': stockcode, 'STOCK_NAME': stockname,
                                                  'SUPPLEMENTAL_PROSPECTUS_URL': url}
                    if "prospectus" in doctype.lower() and "addendum" in doctype.lower():
                        doctype = "addendum prospectus"
                        if stockcode in ipoData.keys():
                            ipoData[stockcode].update({'ADDENDUM_TO_THE_PROSPECTUS_URL': url, 'DATE': dateOfStock})
                        else:
                            ipoData[stockcode] = {'DATE': dateOfStock, 'STOCK_CODE': stockcode, 'STOCK_NAME': stockname,
                                                  'ADDENDUM_TO_THE_PROSPECTUS_URL': url}
                elif "prospectus" in doctype.lower():

                    stockcode = row.find_elements_by_tag_name("td")[1].text
                    stockname = row.find_elements_by_tag_name("td")[2].text
                    url = row.find_element_by_css_selector('td ~ td ~ td ~ td > span ~ div ~ div > a').get_attribute(
                        'href')

                    doctype = "prospectus"
                    if stockcode in ipoData.keys():
                        ipoData[stockcode].update({'PROSPECTUS_URL': url, 'DATE': dateOfStock})
                    else:
                        ipoData[stockcode] = {'DATE': dateOfStock, 'STOCK_CODE': stockcode, 'STOCK_NAME': stockname,
                                              'PROSPECTUS_URL': url}
        # print(ipoData)

        date = rows[0].find_elements_by_tag_name("td")[0].text
        dateOfStock = date[:10]
        logging.info("Last document found was published on " + dateOfStock)
        print("[INFO] Last document found was published on " + dateOfStock)
    else:
        logging.info("Supplementary Listing Documents table is empty - No matches found")
        print("[INFO] Supplementary Listing Documents table is empty - no matches found")

    # Take page screenshot
    screenshot_name = makeScreenshotString("screenshot-hkexnews", download_dir)
    takeScreenshot(screenshot_name, driver)

    for r in ipoData:
        # if r is not empty
        if r:
            ipo_count = ipo_count + 1

    logging.info("Number of Matches found: " + str(ipo_count))
    print("[INFO] Number of Matches found: " + str(ipo_count))

    return ipoData

# Create the directory of which the screenshot will be saved
def makeScreenshotString(screenshot_name, download_dir):
    # Define location and name of screenshot
    screenshot_name = ("{}/" + screenshot_name + ".png").format(download_dir)
    logging.info("Screenshot file: " + screenshot_name)
    print("[INFO] Screenshot file: " + screenshot_name)
    return screenshot_name


def main():
    global error

    # Get current date and time
    now = datetime.now()

    date_today = now.strftime("%d/%m/%Y")
    date_dir = now.strftime("%d-%m-%Y")

    # Test date parameters
    # date_today = "15/02/2018"
    # date_dir = "15-02-2018"

    # Print today's date
    logging.info("Today is " + date_today)
    print("[INFO] Today is: " + date_today)

    # Define location of download directory
    download_dir = get_dir(date_dir)

    # -----------------------------------------------------------------------------------------------------
    # SEARCH - IPO Listing Documents
    # -----------------------------------------------------------------------------------------------------

    ipoData = {}

    driver = openDriver(download_dir)

    # Default run option - no additional parameters entered in command line - search for ALL documents
    if len(sys.argv) == 1:

        suppListingDocData = {}
        allotmentResultsData = {}
        suppInfoRegardingIPOData = {}
        cancellationData = {}

        # Get Supplementary Listing Documents
        selectHeadlineCategory(driver)
        selectSuppListingDocument(driver)
        # time.sleep(10)

        if error == False:
            searchButton(driver)
            if error == False:
                suppListingDocData = getSuppListingDocument(driver, date_today, download_dir)

        # driver.get(website_url)

        # Get Allotment Results / Supplemental Information regarding IPO / Cancellation IPOs
        selectHeadlineCategory(driver)
        selectAnnouncementsAndNotices(driver)

        # # Used for testing - need to manually input date hence the time.sleep
        # time.sleep(20)

        if error == False:
            searchButton(driver)
            if error == False:
                allotmentResultsData = getAllotmentResults(driver, date_today, download_dir)
                suppInfoRegardingIPOData = getSuppInfoRegardingIPO(driver, date_today, download_dir)
                cancellationData = getCancellationIPO(driver, date_today, download_dir)

        # Appending all the dictionaries together
        ipoData = allotmentResultsData.copy()
        ipoData.update(cancellationData)
        ipoData.update(suppInfoRegardingIPOData)
        ipoData.update(suppListingDocData)

        docsSearchedFor = "\n   Supplementary Listing Documents \n   Allotment Results \n " \
                          "  Supplemental Information Regarding IPOs \n   IPO Cancellations (Global Offering not to " \
                          "proceed) "

    elif sys.argv[1] == "SuppListingDoc":
        # Get Supplementary Listing Documents
        selectHeadlineCategory(driver)
        selectSuppListingDocument(driver)

        if error == False:
            searchButton(driver)
            if error == False:
                ipoData = getSuppListingDocument(driver, date_today, download_dir)

        docsSearchedFor = "\n   Supplementary Listing Documents"
    elif sys.argv[1] == "AllotmentResults":
        selectHeadlineCategory(driver)
        selectAnnouncementsAndNotices(driver)

        if error == False:
            searchButton(driver)
            if error == False:
                ipoData = getAllotmentResults(driver, date_today, download_dir)

        docsSearchedFor = "\n   Allotment Results"
    elif sys.argv[1] == "SuppInfoRegardingIPO":
        selectHeadlineCategory(driver)
        selectAnnouncementsAndNotices(driver)

        if error == False:
            searchButton(driver)
            if error == False:
                ipoData = getSuppInfoRegardingIPO(driver, date_today, download_dir)

        docsSearchedFor = "\n   Supplemental Information Regarding IPOs"
    elif sys.argv[1] == "CancellationIPO":
        selectHeadlineCategory(driver)
        selectAnnouncementsAndNotices(driver)

        if error == False:
            searchButton(driver)
            if error == False:
                ipoData = getCancellationIPO(driver, date_today, download_dir)

        docsSearchedFor = "\n   IPO Cancellations (Global Offering not to proceed) "

    sendIPOEmail(ipoData, download_dir, docsSearchedFor)

    time.sleep(10)
    driver.close()


if __name__ == '__main__':
    # print(sys.argv[1])

    # Create logger
    log_format = "%(asctime)s [%(levelname)s][%(name)s][%(filename)s:%(lineno)d] %(message)s"
    logging.basicConfig(filename='ipo.log', filemode='w', level='INFO', format=log_format)

    main()

    logging.shutdown()
