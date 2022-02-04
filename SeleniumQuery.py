#Import Selenium to interact with our target website
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.select import Select
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

#Filter full list of recipients with the helper function below
def sortRecipients(allRecipients, packageSelections):
    cleanedList = []
    for key, value in packageSelections.items():
        keySplit = key.split(", at: ")
        rName = keySplit[0]
        rAddress = keySplit[1]
        packageSize = value[0]
        packageWeight_Lbs = value[1]
        packageWeight_Oz = value[2]
        for eachRecipient in allRecipients[2]:
            if rName == eachRecipient[1] and rAddress == eachRecipient[2]:
                listBuilder = eachRecipient
                listBuilder.append(packageSize)
                listBuilder.append(packageWeight_Lbs)
                listBuilder.append(packageWeight_Oz)
                cleanedList.append(listBuilder)
    print(cleanedList)
    return cleanedList





#TODO update sender input to include the sender row of information
#Need to add it to the input on the SecondIteration.py file, then update the code here to match the new input

def sQuery(recipientInformation, packageSelection):
    senderInformation = recipientInformation[1] #Sender information is at list position in recipients list
    recipients = recipientInformation[2]
    recipientsCleaned = sortRecipients(recipientInformation, packageSelection)
    for eachRow in recipientsCleaned:
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
        senderZip = SecondIteration.parseZipCode(senderInformation[5])
        receiverZip = SecondIteration.parseZipCode(eachRow[5])
        driver.find_element_by_id('senderZipCode').send_keys(senderZip)

        #Reciever Zip Code
        driver.find_element_by_id('recipientZipCode').send_keys(receiverZip)
        driver.find_element_by_id("submit").click()

        #Shipping non-dangerous items?
        driver.find_element_by_id("submit").click()

        #Enter package weight
        myElem = waitForPageLoad(driver, "//input[@id='weightPounds']", delay)
        driver.find_element_by_id('weightPounds').send_keys(eachRow[8])
        driver.find_element_by_id('weightOunces').send_keys(eachRow[9])
        driver.find_element_by_id("submit").click()

        #Select package type for Customs form
        #Sample xPath query to get the target radio button below
        #$x("//div[contains(@class, 'note method-note') and (text()='Large Flat Rate Box')]/ancestor::label/input")
        boxType = eachRow[7]
        xPathQuery = "//div[contains(@class, 'note method-note') and (text()='" + boxType + "')]/ancestor::label/input\")"
        driver.find_element_by_xpath("//div[contains(@class, 'note method-note') and (text()='" + boxType + "')]/ancestor::label/input").click()
        driver.find_element_by_id("submit").click()

        # Add Sender Information here - This should be constant for each run
        driver.find_element_by_id('firstName').send_keys(senderInformation[1].split()[0])# First Name
        driver.find_element_by_id('lastName').send_keys(senderInformation[1].split()[1])#Last Name
        driver.find_element_by_id('companyName').send_keys(senderInformation[1].split()[1])  # Company Name as Last Name
        driver.find_element_by_id('streetAddress').send_keys(senderInformation[2]) #Street Address
        driver.find_element_by_id('city').send_keys(senderInformation[3])
        #TODO get dropdown state from menu
        #driver.find_element_by_id('stateId').selectByVisibleText(senderInformation[4])
        stateSel = Select(driver.find_element_by_id('stateId'))
        stateSel.select_by_visible_text(senderInformation[4])
        #Wait a second for the dropdown to select, to ensure that input is recorded
        delay = 1
        #TODO annonymize phone number and email input
        driver.find_element_by_id('phone').send_keys("1234567890")
        driver.find_element_by_id('email').send_keys("testemail@gmail.com")
        driver.find_element_by_id("submit").click()

        # Add Recipient Information here - This will be unique for each row in the target senders table
        driver.find_element_by_id('firstName').send_keys(eachRow[1].split()[0])# First Name
        driver.find_element_by_id('lastName').send_keys(eachRow[1].split()[1])#Last Name
        driver.find_element_by_id('companyName').send_keys(eachRow[1].split()[1])  # Company Name as Last Name
        driver.find_element_by_id('streetAddress').send_keys(eachRow[2]) #Street Address
        driver.find_element_by_id('city').send_keys(eachRow[3])
        #TODO get dropdown state from menu
        #driver.find_element_by_id('stateId').selectByVisibleText(senderInformation[4])
        stateSel = Select(driver.find_element_by_id('stateId'))
        stateSel.select_by_visible_text(eachRow[4])
        #Wait a second for the dropdown to select, to ensure that input is recorded
        delay = 1
        #TODO annonymize phone number and email input - Make this the same as the sender
        driver.find_element_by_id('phone').send_keys("1234567890")
        driver.find_element_by_id('email').send_keys("testemail@gmail.com")
        driver.find_element_by_id("submit").click()

        # What should USPS do if the package can't be delivered?
        # Return to sender
        driver.find_element_by_xpath("//input[@value='0']").click()
        driver.find_element_by_id("submit").click()

        # What category is the contents of the package? Add comments as needed
        driver.find_element_by_xpath("//input[@value='Gifts']").click()
        driver.find_element_by_id('additionalComments').send_keys("Gifts")

        # Are you a commercial sender?
        driver.find_element_by_xpath("//input[@value='0']").click() #Not a commercial sender
        driver.find_element_by_id("submit").click()

        # Add items to the list of package contents, including:
        # Description, Quantity, Value, Weight,
        driver.find_element_by_xpath("//input[@name='itemDesc']").send_keys("Gifts") #Description
        driver.find_element_by_xpath("//input[@name='itemQty']").send_keys("1") #Quantity
        driver.find_element_by_xpath("//input[@name='unitValue']").send_keys("10") #Value
        driver.find_element_by_xpath("//input[@name='weightPounds']").send_keys(eachRow[8]) #Weight, Pounds
        driver.find_element_by_xpath("//input[@name='weightOunces']").send_keys(eachRow[9]) #Weight, Ounces
        driver.find_element_by_id("submit").click()

        # Confirm the AES Export Option
        driver.find_element_by_id("submit").click()

        # Print the Customs form and save as a PDF to the target folder
        driver.find_element_by_id("submit").click() #The print customs form button has ID Submit
        #At this point, there should be a PDF in the downloads folder

        # TODO - Rename the PDF with some naming logic to help keep the folder organized

