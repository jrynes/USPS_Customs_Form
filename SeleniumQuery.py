#Import Selenium to interact with our target website
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import SecondIteration

import os

# Helper function to slow down selenium and make sure that our page has loaded
def waitForPageLoad(targetDriver, targetCondition, delay):
    try:
        myElem = WebDriverWait(targetDriver, delay).until(EC.presence_of_element_located((By.XPATH, targetCondition)))
        print("Page is ready!")
    except:
        print("Page timed out.")
    return


#TODO update sender input to include the sender row of information
#Need to add it to the input on the SecondIteration.py file, then update the code here to match the new input

def sQuery(recipientInformation, packageSelection):
    senderInformation = recipientInformation[1] #Sender information is at list position in recipients list
    recipients = recipientInformation[2]
    for eachRow in recipients:
        driver = webdriver.Firefox()
        driver.get("https://cfo.usps.com/flow-type")
        # Add delay of 10 seconds to ensure that the target page opens
        delay = 10  # seconds
        try:
            myElem = waitForPageLoad(driver, "//input[@value='militaryToUSA']", delay)
            print ("Page is ready!")
        except TimeoutException:
            print ("Loading took too much time!")

        # How is the object being routed?
        driver.find_element_by_xpath("//input[@value='militaryToUSA']").click()
        driver.find_element_by_id("submit").click()

        # Does the object weigh less than a pound?
        driver.find_element_by_xpath("//input[@value='0']").click()
        driver.find_element_by_id("submit").click()

        #Sender Zip Code
        #TODO Update below
        senderZip = SecondIteration.parseZipCode(sendingAddress[4])
        receiverZip = SecondIteration.parseZipCode(eachRow[4])
        driver.find_element_by_id('senderZipCode').send_keys(senderZip)

        #Reciever Zip Code
        driver.find_element_by_id('recipientZipCode').send_keys(receiverZip)
        driver.find_element_by_id("submit").click()

        #Shipping non-dangerous items?
        driver.find_element_by_id("submit").click()

        #Enter package weight
        myElem = waitForPageLoad(driver, "//input[@id='weightPounds']", delay)
        driver.find_element_by_id('weightPounds').send_keys(eachRow[6])
        driver.find_element_by_id('weightOunces').send_keys(eachRow[7])
        driver.find_element_by_id("submit").click()

        #Select package type for Customs form
        #Sample xPath query to get the target radio button below
        #$x("//div[contains(@class, 'note method-note') and (text()='Large Flat Rate Box')]/ancestor::label/input")
        boxType = eachRow[8]
        xPathQuery = "//div[contains(@class, 'note method-note') and (text()='" + boxType + "')]/ancestor::label/input\")"
        driver.find_element_by_xpath("//div[contains(@class, 'note method-note') and (text()='" + boxType + "')]/ancestor::label/input").click()
        driver.find_element_by_id("submit").click()

        # Add Sender Information here - This should be constant for each run


        # Add Recipient Information here - This will be unique for each row in the target senders table


        # What should USPS do if the package can't be delivered?
        # Return to sender


        # What category is the contents of the package? Add comments as needed


        # Are you a commercial sender?


        # Add items to the list of package contents, including:
        # Description, Quantity, Value, Weight,


        # Confirm the AES Export Option


        # Print the Customs form and save as a PDF to the target folder
        # Rename the PDF with some naming logic to help keep the folder organized
