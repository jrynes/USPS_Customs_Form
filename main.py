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

#Helper class for the check box selection function
#Second Iteration - Use a series of checkboxes to simplify the GUI creation
class selectRecipients_GUI(tk.Toplevel):

    def __init__(self, master, button_dict):
        #Try to set title of window
        #self.master.title("Test")
        self.button_dict = button_dict
        row = len(self.button_dict) + 1
        testResult = []

        for i, key in enumerate(self.button_dict, 1):
            variableName = "VAR" + str(i)
            self.button_dict[key] = tk.IntVar(name=variableName) # set all values of the dict to intvars
            # set the variable of the checkbutton to the value of our dictionary so that our dictionary updates
            #c = tk.Checkbutton(self, text=key, variable=self.button_dict[key],command=lambda: self.cb(self.button_dict[key]))
            c = tk.Checkbutton(self, text=key, variable=self.button_dict[key],
                               command=lambda: self.cb(self.button_dict[key]))
            c.grid(row=i, sticky=tk.W)
            testResult.append(self.button_dict[key])



        #proceed = tk.Button(self.root, text='Proceed', command=self.query_include)
        proceed = tk.Button(self, text='Proceed', command=self.query_include)
        proceed.grid(row=row, sticky=tk.W)

        #quit = tk.Button(self.root, text='Quit', command=self.root.quit)
        quit = tk.Button(self, text='Quit', command=root.quit)
        quit.grid(row=row + 1, sticky=tk.W)

    def cb(self, varItem):
        print("Var value is: " + str(varItem.get()) + ". Var name is " + str(varItem))

    def query_include(self):
        returnList = {}
        for key, value in self.button_dict.items():
            if value.get() == 1:
                print(key, value.get())
                returnList[key] = value
        self.destroy()
        return returnList
                #A.append(key)

    def quit_gui(self):
        self.root.destroy()

# some logic here to have the user select the path where the target CSV file is located
fileTypes = [("CSV File", "*.csv")]

class file_opener(tk.Toplevel):

    def __init__(self, master):
        tk.Toplevel.__init__(self)
        self.master = master

    def fileOpen(self):
        #file = fd.askopenfilename(initialdir=os.getcwd(), filetypes=fileTypes, title="Choose a file.", parent=root)
        self.file = fd.askopenfilename(initialdir=os.getcwd(), filetypes=fileTypes, title="Choose a file.")
        if self.file != "":
            return self.file
        else:
            print ("Error - File not selected")
            return False

#Start tkinter
root = tk.Tk()
root.withdraw()

#Debug
#Get our target information from our CSV file before we start
topLevelTest = tk.Toplevel()
targetCSV_Path = file_opener(topLevelTest).fileOpen()

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
#Create dictionary of values for our GUI
button_dict = {}
divider = ", at: "
for eachRow in recipients:
    strBuilder = str(eachRow[1]) + divider + str(eachRow[2])
    button_dict[strBuilder] = 0

topLevelTest = tk.Toplevel()
gui = selectRecipients_GUI(topLevelTest, button_dict)

root.mainloop()

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
