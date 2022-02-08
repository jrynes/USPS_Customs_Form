#Import statements
import SeleniumQuery

#Import csv to read our addresses from our target spreadsheet
import csv

# Import tkinter to help create our GUI elements for the user
import tkinter as tk
from tkinter import filedialog as fd
from tkinter import ttk
import os

csvInformation = []

# Helper function to parse the zip code contained in our CSV file
def parseZipCode(inputText):
    baseText = inputText.encode("ascii", "ignore")
    revisedText = baseText.decode()
    revisedText = revisedText.replace("\"", "")
    return revisedText


#Helper function to help parse our CSV input
def parseCSV(targetPath):
    labels = []
    sendingAddress = []
    recipients = []
    output = []

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

    output = [labels, sendingAddress, recipients]
    return(output)

def prepareAddress(csvInformation):
    targetIndex = csvInformation[2] #The recipients as marked in our CSV file
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
        cleanedDictionary[key] = [tk.StringVar(value="Select an Option"), tk.StringVar(value="Lbs"),
                                  tk.StringVar(value="Oz"), tk.StringVar(value="Contents")]
    return cleanedDictionary

def parseRecipients(allRecipients, packageSelections):
    output = []
    for eachRecipient in allRecipients:
        for key, value in packageSelections.items():
            strBuilder = key.split(", at: ")
            name = strBuilder[0]
            streetAddress = strBuilder[1]
            if eachRecipient[1] == name and eachRecipient == streetAddress:
                eachRecipient.append(value.get())
                output.append(eachRecipient)
    return output



#Helper method to start our tkinter instance
def main():
    root = tk.Tk()
    root.withdraw()
    app = FileOpener(root)
    app.fileOpen()
    root.mainloop()

    #testVar = parseRecipients(app.recipientsAll, app.packageSelection)
    #print(testVar)
    print(app.data)


# some logic here to have the user select the path where the target CSV file is located
# Using Frame instead of Toplevel, to have a separate window without typical decoration
#class FileOpener(tk.Toplevel):
class FileOpener(tk.Frame):

    def __init__(self, master):
        #tk.Toplevel.__init__(self)
        #tk.Frame.__init__(self)
        self.master = master
        self.frame = tk.Frame(self.master)
        #self.recipientsAll = [] #Check if we can remove, as we're passing the full list of addresses through
        self.packageSelection = {}

    def fileOpen(self):
        #Debug print statement below to check that our Toplevel element is being used here
        #print(self.winfo_exists(my_toplevel_name))
        fileTypes = [("CSV File", "*.csv")]
        file = fd.askopenfilename(initialdir=os.getcwd(), filetypes=fileTypes, title="Choose a file.")
        if file != "":
            print(file)
            recipientInformation = parseCSV(file)
            cleanedInformation = prepareAddress(recipientInformation)
            #self.data.append(cleanedInformation) #Debug method to check that we can append data
            #self.recipientsAll = recipientInformation[2] #set all recipients to callable variable
            #Pass through the recipients and package selection list to be updated later
            gui = selectRecipients_GUI(self.master, cleanedInformation, recipientInformation, self.packageSelection)
        else:
            print ("Error - File not selected")


#Class to have the user select who they want to mail a package to
# Using Toplevel instead of frames, to have a separate window with typical decoration
class selectRecipients_GUI(tk.Toplevel):

    def __init__(self, master, button_dict, recipientsAll, packageSelection):
        self.master = master
        tk.Toplevel.__init__(self, master)
        self.button_dict = button_dict
        row = len(self.button_dict) + 1
        self.returnResult = {}
        self.recipientsAll = recipientsAll
        self.packageSelection = packageSelection

        i = 1

        #Add some instructions to the user here
        headerLabelFormatting = ("Arial", 14, "bold")
        headerLabel = tk.Label(self, text="Please select your package recipients:", pady=3, font=headerLabelFormatting,
                               justify=tk.LEFT)
        headerLabel.grid(row=i, column=0)
        i = i+1

        for key in self.button_dict:
            c = tk.Checkbutton(self, text=key, variable=button_dict[key])
            c.grid(row=i, sticky=tk.W)
            c.var = button_dict[key]
            i = i + 1

        #Proceed button
        proceed = tk.Button(self, text='Proceed', command=lambda: self.query_include())
        proceed.grid(row=i, sticky=tk.W)

        #Quit button
        quit = tk.Button(self, text='Quit', command=lambda: self.quit_gui()) #Add a lambda to only run on click
        quit.grid(row=i + 1, sticky=tk.W)

    def cb(self, varItem):
        print("Var value is: " + str(varItem.get()) + ". Var name is " + str(varItem))

    def query_include(self):
        for key, value in self.button_dict.items():
            if value.get() == 1:
                self.returnResult[key] = value
        self.destroy()
        inputList = preparePackageTypes(self.returnResult)
        s = SelectPackageSize(self.master, inputList, self.recipientsAll, self.packageSelection)

    def quit_gui(self):
        self.master.destroy()

#Class to have the user select their package size from a drop-down list for each recipient
class SelectPackageSize(tk.Toplevel):

    def __init__(self, master, inputDictionary,  recipientsAll, packageSelection):
        super().__init__(master)
        self.master = master
        self.inputDictionary = inputDictionary
        row = len(self.inputDictionary) + 1
        self.returnResult = []
        self.packageOptions = ["Choose your own box", "Small Flat Rate Box",
                               "Medium Flat Rate Box", "Large Flat Rate Box", "APO/FPO Large Flat Rate Box",
                               "Flat Rate Envelope",
                               "Legal Flat Rate Envelope", "Padded Flat Rate Envelope",
                               "Gift Card Flat Rate Envelope", "Small Flat Rate Envelope",
                               "Window Flat Rate Envelope",
                               ]

        self.recipientsAll = recipientsAll
        self.packageSelection = packageSelection

        #Set up a dictionary to update our package selection value on callback
        #TODO Check if we can remove the code below
        '''
        for eachEntry in self.inputDictionary.keys():
            dictionaryBuilder = {}
            strBuilder = eachEntry.split(", at: ")
            addressName = strBuilder[0]
            addressStreet = strBuilder[1]
            packageSize = "default"
            dictionaryBuilder["Name"] = addressName
            dictionaryBuilder["Street Address"] = addressStreet
            dictionaryBuilder["Package Size"] = packageSize
            self.returnResult.append(dictionaryBuilder)
        '''

        # Function to help update our output dictionary when the user makes a dropdown menu selection
        def callback(event):
            print(event)

        i = 1
        headerLabelFormatting = ("Arial", 14, "bold")
        #Add header label with some padding to help inform the user
        headerLabel = tk.Label(self, text="Please select the package type for each recipient:", pady=3, font=headerLabelFormatting)
        headerLabel.grid(row=i, column=1)
        #Add header label for package weight in pounds and ounces
        headerLabel_Pounds = tk.Label(self, text="Package Weight: Pounds", justify=tk.LEFT, pady=3, font=headerLabelFormatting)
        headerLabel_Pounds.grid(row=i, column=3)
        headerLabel_Ounces = tk.Label(self, text="Ounces", pady=3, font=headerLabelFormatting)
        headerLabel_Ounces.grid(row=i, column=4)
        #Add header label for package contents description
        headerLabel_Description = tk.Label(self, text="Package Contents", justify=tk.LEFT, pady=3, font=headerLabelFormatting)
        headerLabel_Description.grid(row=i, column=5)


        i= i+1
        for key, value in self.inputDictionary.items():
            #Separate tkinter variables in the dictionary value
            packageVar = value[0]
            weight_LbsVar = value[1]
            weight_OzVar = value[2]
            packageContents = value[3]
            #Create label for the recipients
            cLabel = tk.Label(self, text=key, justify=tk.LEFT)
            cLabel.grid(row=i, column=1, sticky=tk.W)
            #Create dropdown menu to select the package type
            c = tk.OptionMenu(self, packageVar, *self.packageOptions, command=callback)
            #Set width of the OptionMenu
            c.config(width=20)
            c.grid(row=i, column=2)
            #Add text input box for package weight in pounds and ounces
            cInput_Pounds = tk.Entry(self, textvariable=weight_LbsVar)
            cInput_Pounds.grid(row=i, column=3)
            cInput_Ounces = tk.Entry(self, textvariable=weight_OzVar)
            cInput_Ounces.grid(row=i, column=4)
            #Add text input for package contents description
            cInput_Description = tk.Entry(self, textvariable=packageContents)
            cInput_Description.grid(row=i, column=5)
            print([inputDictionary[key], packageVar.get(), weight_LbsVar.get(), weight_OzVar.get(), cInput_Description.get()])
            i = i + 1

        #Proceed button
        proceed = tk.Button(self, text='Proceed', command=self.query_include)
        proceed.grid(row=i, column=4, sticky=tk.W)

        #Quit button
        quit = tk.Button(self, text='Quit', command=lambda: self.quit_gui()) #Add a lambda here to only run on click
        quit.grid(row=i + 1, column=4, sticky=tk.W)

    def query_include(self):
        cleanedDictionary = {}
        #TODO add check here to make sure that all the values have been set for the inputs
        #Check dropdown
        #Check that input boxes don't have default values, and they are numbers only
        for key, value in self.inputDictionary.items():
            if value[0].get() != "Select an Option":
                self.packageSelection[key] = value
                cleanedDictionary[key] = [val.get() for val in value]
        # Close the window
        self.destroy()
        #Call Selenium Here
        SeleniumQuery.sQuery(self.recipientsAll, cleanedDictionary)

        self.quit_gui()

    def quit_gui(self):
        self.master.destroy()


#Start tkinter
if __name__ == '__main__':
    app1 = main()
