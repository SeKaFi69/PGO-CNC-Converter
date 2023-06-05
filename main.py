#feller axa hass CNC program converter

import sys
import os
import PyQt5 as qt
import time
from PyQt5.QtWidgets import QApplication, QWidget, QInputDialog, QLineEdit, QFileDialog, QMessageBox

#functions
def appendData(filetextPath, fileExt):
    editLog.append("Appending data...")
    textExt.setText(f"File extantion: {fileExt}")
    textPath.setText(f"File textPath: {filetextPath}")
    global Gpath 
    Gpath = filetextPath

def recognizeFile(filetextPath):
    editLog.append("Recognizing file...")
    file = open(filetextPath, "r")
    lines = file.readlines()
    file.close()
    for line in lines:
        #if line contain N7 G01
        if "N7 G01" in line:
            #get rest of line 
            restOfLine = line.split("N7 G01")[1]
            #clear whitespaces
            restOfLine = restOfLine.strip()

            #get first 7 characters
            restOfLine = restOfLine[:7]

            #set CNC Type
            match restOfLine:
                case "G43 G54":
                    inputType = "FELLER"
                case "G43 G58":
                    inputType = "HASS"
                case "G54 G64":
                    inputType = "AXA"
            cncType.setText(f"CNC Type: {inputType}")
            global GinputType
            GinputType = inputType
            break            


def selectFile():
    editLog.append("Selecting file...")
    file , check = QFileDialog.getOpenFileName(None, "Wybierz plik z programem", "", "CNC(*.tap *.MPF)")
    if check:
        editLog.clear()
        cncTypePick.clear()
        fileExt = os.path.splitext(file)[1]

        appendData(file, fileExt)
        recognizeFile(file)
        editLog.append(f"File selected! Reconized as {GinputType}")

        cncTypePick.show()
        btnConvert.show()
        line.show()
        cncTypePick.show()
        cncTypePickLabel.show()
        
        #remove all items from combobox
        
        if GinputType == "FELLER":
            cncTypePick.addItem("AXA")
            cncTypePick.addItem("HASS")
        elif GinputType == "AXA":
            cncTypePick.addItem("FELLER")
            cncTypePick.addItem("HASS")
        elif GinputType == "HASS":
            cncTypePick.addItem("FELLER")
            cncTypePick.addItem("AXA")  

    else:
        sys.exit()

def toFeller(path):
    if GinputType == "HASS":
        editLog.append("=-=-= Converting from HASS to Feller =-=-=")
        editLog.append(path)
        with open(path, "r") as file:
            filedata = file.read()
        
        filedata = filedata.replace("G71", "G21")
        editLog.append("G71 -> G21")
        filedata = filedata.replace("M30", "M02")
        editLog.append("M30 -> M02")
        filedata = filedata.replace("G43 G58","G43 G54") #tylko pierwsze narzędzie
        editLog.append("G43 G58 -> G43 G54")

        # extension .tap
        fileExt = os.path.splitext(path)[1]
        editLog.append("Extension is already .tap")
        path = path.replace(fileExt, "(Feller).tap")

        editLog.append("> Added (Feller) to name")

        with open(path, "w") as file:
            file.write(filedata)
            editLog.append("Convertion succesfull!")

        file.close()

    elif GinputType == "AXA":
        editLog.append("=-=-= Converting from AXA to Feller =-=-=")
        editLog.append(path)
        with open(path, "r") as file:
            filedata = file.read()
        
        
        filedata = filedata.replace("G54 G64", "G43 G54")
        editLog.append("G54 G64 -> G43 G54")
        
        filedata = filedata.replace("G71", "G21")
        editLog.append("G71 -> G21")


        #get filedata until first N1 -1 line
        filedataSmall = filedata.split("N1")[0]
        #delete empty lines
        filedataSmall = filedataSmall.replace("\n\n", "\n")
        editLog.append("Deleted empty lines")

        filedataSmall = filedataSmall.replace(";", "(")
        filedataSmall = filedataSmall.replace("\n", ")\n")
       
        editLog.append("Replaced ; with ( )")

       

        filedata = filedata.replace(filedata.split("N1")[0], filedataSmall)

        # extension .tap
        fileExt = os.path.splitext(path)[1]
        if fileExt != ".tap":
            path = path.replace(fileExt, "(Feller).tap")
            editLog.append("Changed extension to .tap")

        # add % at the beginning and end of the program
        filedata = "%\n" + filedata + "\n%"
        editLog.append("> Added % at the beginning and end of the program")

        with open(path, "w") as file:
            file.write(filedata)
            editLog.append("Convertion succesfull!")
        file.close()

def toAXA(path):
    if GinputType == "HASS":
        editLog.append("=-=-= Converting from HASS to AXA =-=-=")
        editLog.append(path)
        with open(path, "r") as file:
                    filedata = file.read()
        # delete % at the beginning and end of the program
        filedata = filedata.replace("%", "")
        editLog.append("Deleted % at the beginning and end of the program")
        # G43 to G54 G64 for ALL tools
        filedata = filedata.replace("G43 G58", "G54 G64")
        editLog.append("G43 G58 -> G54 G64")


        filedata = filedata.replace("(", ";")
        filedata = filedata.replace(")", "")
        editLog.append("Replaced ( with ; and deleted )")

        if ";;" in filedata:
            filedata = filedata.replace(";;", ";")
            editLog.append("Removed double ;")
        
        editLog.append("> Added ; before the description so that the machine does not read it")
        # at the end of the program we change M30 to M02
        filedata = filedata.replace("M30", "M02")
        editLog.append("M30 -> M02")
        # extension .MPF
        fileExt = os.path.splitext(path)[1]
        if fileExt != ".MPF":
            path = path.replace(fileExt, "(AXA).MPF")
            editLog.append("Changed extension to .MPF")

        with open(path, "w") as file:
            file.write(filedata)
            editLog.append("Convertion succesfull!")  
        file.close()
    
    elif GinputType == "FELLER":

        editLog.append("=-=-= Converting from Feller to AXA =-=-=")
        editLog.append(path)
        with open(path, "r") as file:
                    filedata = file.read()
        # delete % at the beginning and end of the program
        filedata = filedata.replace("%", "")
        editLog.append("Deleted % at the beginning and end of the program")
        # G43 G54 to G54 G64 for ALL tools
        filedata = filedata.replace("G43 G54", "G54 G64")
        editLog.append("G43 G54 -> G54 G64")

        filedata = filedata.replace("(", ";")
        filedata = filedata.replace(")", "")
        
        
        editLog.append("> Added ; before the description so that the machine does not read it")
        # at the end of the program we change M30 to M02
        filedata = filedata.replace("M30", "M02")
        editLog.append("M30 -> M02")
        
        # change name to name + (AXA) with extension .MPF
        fileExt = os.path.splitext(path)[1]
        if fileExt != ".MPF":
            path = path.replace(fileExt, "(AXA).MPF")
            editLog.append("Changed extension to .MPF")

        with open(path, "w") as file:
            file.write(filedata)
            editLog.append("Convertion succesfull!")  
        file.close()

def toHass(path):
# reverse of to feller

    if GinputType == "FELLER":
        editLog.append("=-=-= Converting from Feller from HASS =-=-=")
        editLog.append(path)
        with open(path, "r") as file:
            filedata = file.read()
        
        filedata = filedata.replace("G21", "G71")
        editLog.append("G21 -> G71")
        
        filedata = filedata.replace("G43 G54","G43 G58") 
        editLog.append("G43 G54 -> G43 G58")

        filedata = filedata.replace("M02", "M30")
        editLog.append("M02 -> M30")

        # edit path (HASS)

        editLog.append("Extension is already .tap")
        fileExt = os.path.splitext(path)[1]

        
        path = path.replace(fileExt, "(HASS).tap")
        editLog.append("(> Added (HASS) to the name)")
        

        with open(path, "w") as file:
            file.write(filedata)
            editLog.append("Convertion succesfull!")  

        file.close()
    elif GinputType == "AXA":
        
        editLog.append("=-=-= Conve rting from AXA to HASS =-=-=")
        editLog.append(path)
        with open(path, "r") as file:
            filedata = file.read()
        
        filedata = filedata.replace("G54 G64", "G43 G58")
        editLog.append("G54 G64 -> G43 G58")

        filedata = filedata.replace("M02", "M30")
        editLog.append("M02 -> M30")

        fileExt = os.path.splitext(path)[1]
        if fileExt != ".tap":
            path = path.replace(fileExt, "(HASS).tap")
            editLog.append("Changed extension to .tap")
        
         #get filedata until first N1 -1 line
        filedataSmall = filedata.split("N1")[0]
        #delete empty lines
        filedataSmall = filedataSmall.replace("\n\n", "\n")
        editLog.append("Deleted empty lines")

        filedataSmall = filedataSmall.replace(";", "(")
        filedataSmall = filedataSmall.replace("\n", ")\n")
       
        editLog.append("Replaced ; with ( )")

        filedata = filedata.replace(filedata.split("N1")[0], filedataSmall)

        filedata = "%\n" + filedata + "\n%"
        editLog.append("> Added % at the beginning and end of the program")    


        with open(path, "w") as file:
            file.write(filedata)
            editLog.append("Convertion succesfull!")
        #add % at the beginning and end of the program



        file.close()



        
        

        
        
    
def convert(inputType):
    GoutputType = cncTypePick.currentText()
    if inputType == GoutputType:
        editLog.append("ERROR: Input and output type are the same")
        return
    else:
        match inputType:
            case "HASS":
                match GoutputType:
                    case "FELLER":
                        toFeller(Gpath)
                    case "AXA":
                        toAXA(Gpath)
            case "FELLER":
                match GoutputType:
                    case "HASS":
                        toHass(Gpath)
                    case "AXA":
                        toAXA(Gpath)
            case "AXA":
                match GoutputType:
                    case "HASS":
                        toHass(Gpath)
                    case "FELLER":
                        toFeller(Gpath)
    editLog.append("Done!")
    QMessageBox.about(window, "Done!", "Done!")
     
App = QApplication(sys.argv)
window = QWidget()
#window settings
window.setGeometry(100, 100, 800, 600)
window.setStyleSheet("background-color: #2b2b2b; color: #ffffff;")
window.setWindowTitle('Feller AXA Hass CNC Program Converter')
#center of the screen
centerPoint = qt.QtWidgets.QDesktopWidget().availableGeometry().center()
window.move(centerPoint.x() - 400, centerPoint.y() - 300)

#variables
fileExt = ""
toolNumber = 0
clickCount = 0

#labels
title = qt.QtWidgets.QLabel(window)
title.setFont(qt.QtGui.QFont('Arial', 15))
title.setText("Feller AXA Hass CNC Program Converter")
title.move(160, 25)

#default buttons

#select file button
btnSelect = qt.QtWidgets.QPushButton('Select File', window)
btnSelect.move(20, 60)
btnSelect.clicked.connect(selectFile)
btnSelect.setFont(qt.QtGui.QFont('Arial', 10))
btnSelect.setFixedWidth(120)

#convert button
btnConvert = qt.QtWidgets.QPushButton('Convert', window)
btnConvert.move(20, 160)
btnConvert.setFont(qt.QtGui.QFont('Arial', 10))
btnConvert.setFixedWidth(120)
btnConvert.clicked.connect(lambda: convert(GinputType))
btnConvert.hide()

#display extension of selected file
textExt = qt.QtWidgets.QLabel(window)
textExt.setFont(qt.QtGui.QFont('Arial', 10))
textExt.setFixedWidth(600)
textExt.move(160, 60)

#display path of selected file
textPath = qt.QtWidgets.QLabel(window)
textPath.setFont(qt.QtGui.QFont('Arial', 10))
textPath.setFixedWidth(600)

textPath.move(160, 90)

#display CNC Type
cncType = qt.QtWidgets.QLabel(window)
cncType.setFont(qt.QtGui.QFont('Arial', 10))
cncType.setFixedWidth(600)
cncType.move(160, 120)

#line
line = qt.QtWidgets.QFrame(window)
line.setGeometry(0, 150, 800, 1)
line.setStyleSheet("background-color: #ffffff;")
line.setFrameShape(qt.QtWidgets.QFrame.HLine)
line.setFrameShadow(qt.QtWidgets.QFrame.Sunken)
line.hide()

#btn log test
btnLog = qt.QtWidgets.QPushButton('Log', window)
btnLog.move(20, 200)
btnLog.setFont(qt.QtGui.QFont('Arial', 10))
btnLog.setFixedWidth(120)
btnLog.clicked.connect(lambda: editLog.append("test"))

#label for CNC Type Pick
cncTypePickLabel = qt.QtWidgets.QLabel(window)
cncTypePickLabel.setFont(qt.QtGui.QFont('Arial', 10))
cncTypePickLabel.setText("To CNC Type:")
cncTypePickLabel.move(160, 165)
cncTypePickLabel.hide()

#CNC Type Pick
cncTypePick = qt.QtWidgets.QComboBox(window)
font = qt.QtGui.QFont('Arial', 10)
font.setPointSize(10)
cncTypePick.setFont(font)
cncTypePick.move(280, 160)
cncTypePick.setFixedWidth(200)
cncTypePick.setFixedHeight(30)

#show only unique CNC types

cncTypePick.addItem("Pick CNC Type")
cncTypePick.addItem("FELLER")
cncTypePick.addItem("AXA")
cncTypePick.addItem("HASS")
cncTypePick.hide()

#edit log
editLog = qt.QtWidgets.QTextEdit(window)
editLog.setFont(font)
editLog.move(20, 200)
editLog.setFixedWidth(760)
editLog.setFixedHeight(390)


window.show()
App.exec_()