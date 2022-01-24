#Import statements
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

#Helper function to help parse our CSV input
def parseCSV(targetPath):
    labels = []
    sendingAddress = []
    recipients = []

    with open(targetPath) as fd:
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

    return([labels, sendingAddress, recipients])

def prepareAddress(csvInformation):
    targetIndex = csvInformation[2]
    button_dict = {}
    divider = ", at: "
    for eachRow in targetIndex:
        strBuilder = str(eachRow[1]) + divider + str(eachRow[2])
        button_dict[strBuilder] = tk.IntVar(name=strBuilder)
    return button_dict

def preparePackageTypes(inputDictionary):
    cleanedDictionary = {}
    for key in inputDictionary.keys():
        #keyVal = inputDictionary[key]
        cleanedDictionary[key] = tk.StringVar(value="Select an Option")
    return cleanedDictionary

#Helper method to start our tkinter instance
def main():
    root = tk.Tk()
    root.withdraw()
    app = FileOpener(root).fileOpen()
    root.mainloop()


# some logic here to have the user select the path where the target CSV file is located
# Using Frame instead of Toplevel, to have a separate window without typical decoration
#class FileOpener(tk.Toplevel):
class FileOpener(tk.Frame):

    def __init__(self, master):
        #tk.Toplevel.__init__(self)
        #tk.Frame.__init__(self)
        self.master = master
        self.frame = tk.Frame(self.master)

    def fileOpen(self):
        #Debug print statement below to check that our Toplevel element is being used here
        #print(self.winfo_exists(my_toplevel_name))
        fileTypes = [("CSV File", "*.csv")]
        #file = fd.askopenfilename(initialdir=os.getcwd(), filetypes=fileTypes, title="Choose a file.", parent=root)
        file = fd.askopenfilename(initialdir=os.getcwd(), filetypes=fileTypes, title="Choose a file.")
        if file != "":
            print(file)
            recipientInformation = parseCSV(file)
            cleanedInformation = prepareAddress(recipientInformation)
            gui = selectRecipients_GUI(self.master, cleanedInformation)
            #return file
        else:
            print ("Error - File not selected")
            #return False

''' Debug method below
#Class to store our returned variable from the recipient selection
class RecipientSelection():
    def __init__ (self):
        self.returnedVariable = None

    def returnVariable (self, x):
        self.returnedVariable = x

#Call our class here
returnVar = RecipientSelection ()
'''


#Class to have the user select who they want to mail a package to
# Using Toplevel instead of frames, to have a separate window with typical decoration
class selectRecipients_GUI(tk.Toplevel):

    #def __init__(self, master, button_dict):
    def __init__(self, master, button_dict):
        self.master = master
        tk.Toplevel.__init__(self, master)
        self.button_dict = button_dict
        row = len(self.button_dict) + 1
        self.returnResult = {}

        i = 1

        for key in self.button_dict:
            #c = tk.Checkbutton(self, text=key, variable=button_dict[key])
            c = tk.Checkbutton(self, text=key, variable=button_dict[key])
            c.grid(row=i, sticky=tk.W)
            c.var = button_dict[key]
            #testResult.append([self.button_dict[key], self.button_dict[key].get()])
            print([button_dict[key], button_dict[key].get()])
            i = i + 1

        #Proceed button
        proceed = tk.Button(self, text='Proceed', command=self.query_include)
        #proceed = tk.Button(self text='Proceed', command=self.query_include)
        proceed.grid(row=row, sticky=tk.W)

        #Quit button
        quit = tk.Button(self, text='Quit', command=lambda: self.quit_gui())
        quit.grid(row=row + 1, sticky=tk.W)

    def cb(self, varItem):
        print("Var value is: " + str(varItem.get()) + ". Var name is " + str(varItem))

    def query_include(self):
        #returnList = {}
        #s = self.returnList
        self.returnResult
        #try:
        for key, value in self.button_dict.items():
            if value.get() == 1:
                #print(key, value.get())
                self.returnResult[key] = value
            self.destroy()
        #Try to open a new window here
        #topLevelTest_3 = tk.Toplevel()
        #topLevelTest_3.title = "Test"
        inputList = preparePackageTypes(self.returnResult)
        #s = SelectPackageSize(topLevelTest_3, inputList)
        s = SelectPackageSize(inputList)
            #self.foo.destroy()
            #root.destroy()
            #return
        #except:
            #print("Error A")
            #root.destroy()

    def quit_gui(self):
        #self.root.destroy()
        self.master.destroy()

#Class to have the user select their package size from a drop-down list for each recipient
class SelectPackageSize(tk.Toplevel):

    #def __init__(self, master, inputList):
    def __init__(self, master, inputList):
        #tk.Toplevel.__init__(self, root)
        #super().__init__(master)
        #tLevel = tk.Toplevel(master)
        self.inputList = inputList
        #row = len(self.inputList) + 1
        self.returnResult = {}
        self.packageOptions = ["Choose your own box", "Small Flat Rate Box",
                               "Medium Flat Rate Box", "Large Flat Rate Box", "APO/FPO Large Flat Rate Box",
                               "Flat Rate Envelope",
                               "Legal Flat Rate Envelope", "Padded Flat Rate Envelope",
                               "Gift Card Flat Rate Envelope", "Small Flat Rate Envelope",
                               "Window Flat Rate Envelope",
                               ]


        i = 1
        #Add header label with some padding to help inform the user
        headerLabel = tk.Label(self, text="Please select the package type for each recipient:", pady=3)
        headerLabel.grid(row=i, column=1)
        i= i+1
        for key, value in self.inputList.items():
            #c = tk.Checkbutton(self, text=key, variable=button_dict[key])
            cLabel = tk.Label(self, text=key, justify=tk.LEFT)
            cLabel.grid(row=i, column=1, sticky=tk.W)
            c = tk.OptionMenu(self, value, *self.packageOptions)
            c.grid(row=i, column=2, sticky=tk.W)
            #c.var = button_dict[key]
            #testResult.append([self.button_dict[key], self.button_dict[key].get()])
            print([inputList[key], inputList[key].get()])
            i = i + 1

        #Proceed button
        proceed = tk.Button(self, text='Proceed', command=self.query_include)
        proceed.grid(row=i, column=2, sticky=tk.W)

        #Quit button
        #quit = tk.Button(self, text='Quit', command=root.quit)
        #quit.grid(row=i + 1, column=2, sticky=tk.W)

        def query_include(self):
            # returnList = {}
            # s = self.returnList
            self.returnResult
            try:
                for key, value in self.button_dict.items():
                    if value.get() == 1:
                        # print(key, value.get())
                        self.returnResult[key] = value
                self.destroy()
                # self.foo.destroy()
                # root.destroy()
                # return
            except:
                print("Error A")
                # root.destroy()

    def query_include(self):
        #returnList = {}
        #s = self.returnList
        self.returnResult
        try:
            for key, value in self.button_dict.items():
                if value.get() == 1:
                    #print(key, value.get())
                    self.returnResult[key] = value
            self.destroy()
            #self.foo.destroy()
            #root.destroy()
            #return
        except:
            print("Error A")
            #root.destroy()


#Start tkinter
if __name__ == '__main__':
    main()


''' OLD CODE BELOW
#root = tk.Tk()
#Hide the root window, as we're using Frames and Toplevel elements
#root.withdraw()

#Get our target information from our CSV file as we start
#Try creating a frame instead of a Toplevel for the file dialog
#topLevelTest = tk.Frame(root)
#targetCSV_Path = FileOpener(topLevelTest).fileOpen()

#Parse our CSV file
#recipientInformation = parseCSV(targetCSV_Path)
#cleanedInformation = prepareAddress(recipientInformation)

#Call our class to have the user select who to mail to
#topLevelTest_2 = tk.Frame(root)
#gui = selectRecipients_GUI(topLevelTest_2, cleanedInformation)
#gui = selectRecipients_GUI(cleanedInformation)
#testVal = gui.returnResult
#print(testVal)

#Align our output from the previous function before selecting target package type
#inputList = preparePackageTypes(testVal)

#Create new Toplevel element to have user select package type for each recipient
#topLevelTest_3 = tk.Frame(root)
#gui_3 = SelectPackageSize(topLevelTest_3, inputList)



#----Mainloop keeps forms updated and listens for user input--
#root.mainloop()

#print(testVal)

#print(inputList)

'''