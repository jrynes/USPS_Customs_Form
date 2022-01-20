#Import Selenium to interact with our target website
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
#Import csv to read our addresses from our target spreadsheet
import csv
# Import tkinter to help create our GUI elements for the user
import tkinter as tk
from tkinter import filedialog as fd
from tkinter import ttk
import os


# Helper function to parse the zip code contained in our CSV file
def parseZipCode(inputText):
    baseText = inputText.encode("ascii", "ignore")
    revisedText = baseText.decode()
    revisedText = revisedText.replace("\"", "")
    return revisedText

# Helper function to slow down selenium and make sure that our page has loaded
def waitForPageLoad(targetDriver, targetCondition, delay):
    try:
        myElem = WebDriverWait(targetDriver, delay).until(EC.presence_of_element_located((By.XPATH, targetCondition)))
        print("Page is ready!")
    except:
        print("Page timed out.")
    return

# NOT CURRENTLY USED - Helper function to help select our package type
# def selectPackageType(webDriver, radioGroupName, valueToFind):
#     radioGroup = webDriver.findElements(By.name(radioGroupName))
#     #try:
#     for eachItem in radioGroup:
#         if radioGroup.get(eachItem).getAttribute("note method-note").equals(valueToFind):
#             radioGroup.get(eachItem).click()
#             return
#     #except:
#         #print("Error, value not found")

#TODO: Add some logic here to have the user select the path where the target CSV file is located
# Use a tree view function from tkinter to achieve this
def selectRecipients(columnNames, rowContent):
    root = tk.Tk()
    root.title('Select Package Recipients:')
    root.geometry('600x200')

    # define columns
    #columnNames = ('first_name', 'last_name', 'email')
    #Clean our column names from our CSV file. If the header contains a space, replace it with an underscore for processing
    cleanedColumnNames = [sub.replace(" ", "_") for sub in columnNames]
    joinedColumnNames = ",".join(cleanedColumnNames)



    tree = ttk.Treeview(root, columns=cleanedColumnNames, show='headings')

    # define headings
    #tree.heading('first_name', text='First Name')
    for originalName, cleanedName in zip(columnNames, cleanedColumnNames):
        tree.heading(cleanedName, text=originalName)

    for eachRowItem in rowContent:
        tree.insert("",tk.END,values=eachRowItem)

    tree.grid(row=0, column=0, sticky='nsew')

    root.mainloop()

fileTypes = [("CSV File", "*.csv")]

def file_opener():
    root = tk.Tk()
    root.withdraw()
    file = fd.askopenfilename(initialdir=os.getcwd(), filetypes=fileTypes, title="Choose a file.")
    if file:
        return file
    else:
        print ("Error - File not selected")
        return False

#Get our target information from our CSV file before we start
targetCSV_Path = file_opener()
#targetCSV_Path = '/Users/Jeff/Documents/Customs_Form_v1.csv'

labels = []
sendingAddress = []
recipients = []

with open(targetCSV_Path) as fd:
    reader = csv.reader(fd)
    for idx, row in enumerate(reader):
        if idx == 0:
            labels = row
        elif row[0] == "Sender":
            if len(sendingAddress) == 0:
                sendingAddress = row
            else:
                print("Error - Two rows are marked as the package sender.")
        elif row[0] == "Reciever":
            if row not in recipients:
                recipients.append(row)
            else:
                print("Error - Duplicate addresses are in the source CSV file.")

# TODO: Add some logic here to present a checkbox for the user to select which people to send the package to
checkedRecipients = selectRecipients(labels, recipients)


for eachRow in recipients:
    driver = webdriver.Firefox()
    driver.get("https://cfo.usps.com/flow-type")
    # Add delay of 10 seconds to ensure that the target page opens
    delay = 10  # seconds
    try:
        # myElem = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.XPATH, "//input[@value='militaryToUSA']")))
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
    senderZip = parseZipCode(sendingAddress[4])
    #string_encode = senderZip_Base.encode("ascii", "ignore")
    #string_decode = string_encode.decode()
    #senderZip = string_decode
    receiverZip = parseZipCode(eachRow[4])
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
    #driver.find_element_by_xpath("//div[contains(@class, 'note method-note') and (text()='Large Flat Rate Box')]/ancestor::label/input").click()
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
