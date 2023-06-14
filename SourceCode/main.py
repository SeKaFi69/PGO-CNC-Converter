#feller axa hass CNC program converter

import sys
import os
import PyQt5 as qt
from PyQt5.QtWidgets import QApplication, QWidget, QFileDialog, QMessageBox
import re

#functions
def Text(text):
    return f"<p style='margin:0;padding:0;'>{text}</p>"
def blueText(text):
    return f"<p style='color: #52fffc; margin: 0; padding: 0;'>{text}</p>"
def errorText(text):
    return f"<p style='color: #ff0000; margin: 0; padding: 0;'>{text}</p>"
def orangeText(text):
    return f"<p style='color: #ffba7a; margin: 0; padding: 0;'>{text}</p>"


def appendData(filetextPath, fileExt):
    editLog.append("Dołączanie pliku...")
    textExt.setText(f"Rozszerzenie pliku: {fileExt}")
    textPath.setText(f"Ścieżka do pliku: {filetextPath}")
    global Gpath 
    Gpath = filetextPath

def recognizeFile(filetextPath):
    editLog.append("Rozpoznawanie typu...")
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
            
            global GinputType
            GinputType = inputType
            cncType.setText(f"Typ CNC:  {inputType}")

            break            


def selectFile():
    editLog.append("Wybieranie pliku...")
    file , check = QFileDialog.getOpenFileName(None, "Wybierz plik z programem", "", "CNC(*.tap *.MPF)")
    if check:
        editLog.clear()
        cncTypePick.clear()
        fileExt = os.path.splitext(file)[1]
        global GfileExt
        GfileExt = fileExt

        appendData(file, fileExt)
        recognizeFile(file)
        editLog.append(f"Rozpoznano plik jako {blueText(GinputType)}")
        
        preview.append(f"<p style='margin:0;padding:0;color: #ffba7a;'>Przed konwertem: {GinputType}</p>")        

        searchItems= ["G71", "G21", "M02", "M30", "N7 G01 G43 G58", "N7 G01 G43 G54", "N7 G01 G54 G64"]
        searchStrategy = "normal"
        with open(Gpath, "r") as file:
            for line in file:
                regex = re.compile("(%s)" % "|".join(map(re.escape, searchItems)))
                if regex.search(line):
                    # preview.append(line)
                    if searchStrategy == "normal":
                        #if searchItems in line:
                        for item in searchItems:
                            if item in line:
                                if item not in preview.toPlainText():
                                    preview.append(item)        
        preview.append(GfileExt)

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
        editLog.append("Anulowanie wybierania!")
        return

def toFeller(path):
    if GinputType == "HASS":
        editLog.append(blueText("=-=-= Konwertowanie z HASS na Feller =-=-="))
        editLog.append(Text(path))
        with open(path, "r") as file:
            filedata = file.read()
        
        filedata = filedata.replace("G71", "G21")
        editLog.append(Text("G71 -> G21"))
        filedata = filedata.replace("M30", "M02")
        editLog.append(Text("M30 -> M02"))
        filedata = filedata.replace("G43 G58","G43 G54") #tylko pierwsze narzędzie
        editLog.append(Text("G43 G58 -> G43 G54"))

        # extension .tap
        fileName = os.path.splitext(path)[0]
        fileExt = os.path.splitext(path)[1]

        if fileExt == ".tap":
            editLog.append(errorText("Rozszerzenie jest już .tap"))

        # name + (Feller)
        if "(AXA)" in fileName:
            path = path.replace("(AXA)", "(Feller)")
        elif "(HASS)" in fileName:
            path = path.replace("(HASS)", "(Feller)")
        else:
            path = path.replace(fileName, fileName + "(Feller)")


        editLog.append(Text("Dodano (Feller) do nazwy pliku"))

        with open(path, "w") as file:
            file.write(filedata)
            editLog.append("Plik zmnieniony pomyślnie!")

        file.close()

    elif GinputType == "AXA":
        editLog.append(blueText("=-=-= Konwertowanie z AXA na Feller =-=-="))
        editLog.append(Text(path))
        with open(path, "r") as file:
            filedata = file.read()
        
        
        filedata = filedata.replace("G54 G64", "G43 G54")
        editLog.append(Text("G54 G64 -> G43 G54"))
        
        filedata = filedata.replace("G71", "G21")
        editLog.append(Text("G71 -> G21"))


        #get filedata until first N1 -1 line
        filedataSmall = filedata.split("N1")[0]
        #delete empty lines
        filedataSmall = filedataSmall.replace("\n\n", "\n")
        editLog.append(Text("Usunięto puste linie"))

        filedataSmall = filedataSmall.replace(";", "(")
        filedataSmall = filedataSmall.replace("\n", ")\n")
       
        editLog.append(Text("Zamieniono ; na ()"))
        filedata = filedata.replace(filedata.split("N1")[0], filedataSmall)

        # add % at the beginning and end of the program
        filedata = "%\n" + filedata + "\n%"
        editLog.append(Text("Dodano % na początku i końcu programu"))

        # extension .tap
        fileName = os.path.splitext(path)[0]
        fileExt = os.path.splitext(path)[1]

        if fileExt == ".tap":
            editLog.append(errorText("Rozszerzenie jest już .tap"))
        else:
            path = path.replace(fileExt, ".tap")
            editLog.append(Text("Zmieniono rozszerzenie na .tap"))



        # name + (Feller)
        if "(AXA)" in fileName:
            path = path.replace("(AXA)", "(Feller)")
        elif "(HASS)" in fileName:
            path = path.replace("(HASS)", "(Feller)")
        else:
            path = path.replace(fileName, fileName + "(Feller)")


        editLog.append(Text("Dodano (Feller) do nazwy pliku"))
       

        with open(path, "w") as file:
            file.write(filedata)
            editLog.append(blueText("Plik zmnieniony pomyślnie!"))
        file.close()

def toAXA(path):
    if GinputType == "HASS":
        editLog.append(blueText("=-=-= Konwertowanie z HASS na AXA =-=-="))
        editLog.append(path)
        with open(path, "r") as file:
                    filedata = file.read()
        # delete % at the beginning and end of the program
        filedata = filedata.replace("%", "")
        editLog.append(Text("Usunięto % na początku i końcu programu"))
        # G43 to G54 G64 for ALL tools
        filedata = filedata.replace("N7 G43 G58", "N7 G54 G64")
        editLog.append(Text("G43 G58 -> G54 G64"))


        filedata = filedata.replace("(", ";")
        filedata = filedata.replace(")", "")
        editLog.append(Text("Zamieniono () na ;"))

        if ";;" in filedata:
            filedata = filedata.replace(";;", ";")
            editLog.append(Text("Usunięto podwójne ;"))
        
        # at the end of the program we change M30 to M02
        filedata = filedata.replace("M30", "M02")
        editLog.append(Text("M30 -> M02"))

         # extension .MPF
        fileName = os.path.splitext(path)[0]
        fileExt = os.path.splitext(path)[1]

        if fileExt == ".MPF":
            editLog.append(errorText("Rozszerzenie jest już .MPF"))
        else:
            path = path.replace(fileExt, ".MPF")
            editLog.append(Text("Zmieniono rozszerzenie na .MPF"))



        # name + (Feller)
        if "(Feller)" in fileName:
            path = path.replace("(Feller)", "(AXA)")
        elif "(HASS)" in fileName:
            path = path.replace("(HASS)", "(AXA)")
        else:
            path = path.replace(fileName, fileName + "(AXA)")


        editLog.append(Text("Dodano (AXA) do nazwy pliku"))
        with open(path, "w") as file:
            file.write(filedata)
            editLog.append(blueText("Plik zmnieniony pomyślnie!")  )
        file.close()
    
    elif GinputType == "FELLER":

        editLog.append(blueText("=-=-= Konwertowanie z FELLER na AXA =-=-="))
        editLog.append(path)
        with open(path, "r") as file:
                    filedata = file.read()

        # delete % at the beginning and end of the program
        filedata = filedata.replace("%", "")
        editLog.append(Text("Usunięto % na początku i końcu programu"))

        # G43 G54 to G54 G64 for ALL tools
        filedata = filedata.replace("N7 G43 G54", "N7 G54 G64")
        editLog.append(Text("G43 G54 -> G54 G64"))

        filedata = filedata.replace("(", ";")
        filedata = filedata.replace(")", "")
        
        
        editLog.append(Text("Zamieniono () na ;"))
        # at the end of the program we change M30 to M02
        filedata = filedata.replace("M30", "M02")
        editLog.append(Text("M30 -> M02"))
        
        # extension .tap
        fileName = os.path.splitext(path)[0]
        fileExt = os.path.splitext(path)[1]

        if fileExt == ".MPF":
            editLog.append(errorText("Rozszerzenie jest już .MPF"))
        else:
            path = path.replace(fileExt, ".MPF")
            editLog.append(Text("Zmieniono rozszerzenie na .MPF"))



        # name + (AXA)
        if "(Feller)" in fileName:
            path = path.replace("(Feller)", "(AXA)")
        elif "(HASS)" in fileName:
            path = path.replace("(HASS)", "(AXA)")
        else:
            path = path.replace(fileName, fileName + "(AXA)")


        editLog.append(Text("Dodano (AXA) do nazwy pliku"))
        with open(path, "w") as file:
            file.write(filedata)
            editLog.append(blueText("Plik zmnieniony pomyślnie!")  )
        file.close()

def toHass(path):
# reverse of to feller

    if GinputType == "FELLER":
        editLog.append(blueText("=-=-= Konwertowanie z FELLER na HASS =-=-="))
        editLog.append(path)
        with open(path, "r") as file:
            filedata = file.read()
        
        filedata = filedata.replace("G21", "G71")
        editLog.append(Text("G21 -> G71"))
        
        filedata = filedata.replace("G43 G54","G43 G58") 
        editLog.append(Text("G43 G54 -> G43 G58"))

        filedata = filedata.replace("M02", "M30")
        editLog.append(Text("M02 -> M30"))

        # extension .tap
        fileName = os.path.splitext(path)[0]
        fileExt = os.path.splitext(path)[1]

        if fileExt == ".tap":
            editLog.append(errorText("Rozszerzenie jest już .tap"))
        else:
            path = path.replace(fileExt, ".tap")
            editLog.append(Text("Zmieniono rozszerzenie na .tap"))

        # name + (HASS)
        if "(AXA)" in fileName:
            path = path.replace("(AXA)", "(HASS)")
        elif "(Feller)" in fileName:
            path = path.replace("(Feller)", "(HASS)")
        else:
            path = path.replace(fileName, fileName + "(HASS)")


        editLog.append(Text("Dodano (HASS) do nazwy pliku"))

        with open(path, "w") as file:
            file.write(filedata)
            editLog.append(blueText("Plik zmnieniony pomyślnie!")  )

        file.close()
    elif GinputType == "AXA":
        
        editLog.append(blueText("=-=-= Konwertowanie z AXA na HASS =-=-="))
        editLog.append(path)
        with open(path, "r") as file:
            filedata = file.read()
        
        filedata = filedata.replace("G54 G64", "G43 G58")
        editLog.append(Text("G54 G64 -> G43 G58"))

        filedata = filedata.replace("M02", "M30")
        editLog.append(Text("M02 -> M30"))
        
        #get filedata until first N1 -1 line
        filedataSmall = filedata.split("N1")[0]

        #delete empty lines
        filedataSmall = filedataSmall.replace("\n\n", "\n")
        editLog.append(Text("Usunięto puste linie"))

        filedataSmall = filedataSmall.replace(";", "(")
        filedataSmall = filedataSmall.replace("\n", ")\n")
       
        editLog.append(Text("Zamieniono ; na ()"))

        filedata = filedata.replace(filedata.split("N1")[0], filedataSmall)

        filedata = "%\n" + filedata + "\n%"
        editLog.append(Text("Dodano % na początku i końcu programu")  )  

 # extension .tap
        fileName = os.path.splitext(path)[0]
        fileExt = os.path.splitext(path)[1]

        if fileExt == ".tap":
            editLog.append(errorText("Rozszerzenie jest już .tap"))
        else:
            path = path.replace(fileExt, ".tap")

        if "(AXA)" in fileName:
            path = path.replace("(AXA)", "(HASS)")
        elif "(Feller)" in fileName:
            path = path.replace("(Feller)", "(HASS)")
        else:
            path = path.replace(fileName, fileName + "(HASS)")

        editLog.append(Text("Dodano (HASS) do nazwy pliku"))

        with open(path, "w") as file:
            file.write(filedata)
            editLog.append(blueText("Plik zmnieniony pomyślnie!"))
        file.close()



        
        

        
        
    
def convert(inputType):
    global GoutputType
    GoutputType = cncTypePick.currentText()
    global GoutputExt



    if inputType == "":
        editLog.append(errorText("Błąd: Nie wybrano pliku wejściowego"))
        return
    elif GoutputType == "":
        editLog.append(errorText("Błąd: Nie wybrano pliku wyjściowego"))
        return
    elif inputType == GoutputType:
        editLog.append(errorText("Błąd: Wybrano ten sam typ pliku"))
        return
    
    else:
        preview.append(blueText("=-=-= Konwertowanie =-=-="))
        preview.append(orangeText("Ścieżka pliku: ") + Gpath)
        preview.append(orangeText("Typ pliku wejściowego: ") + GinputType)
        preview.append(orangeText("Typ pliku wyjściowego: ") + GoutputType)
        preview.append(blueText("=-=-=-=-=-=-=-=-=-=-=-=-="))
        match inputType:
            case "HASS":
                match GoutputType:
                    case "FELLER":
                        toFeller(Gpath)
                        GoutputExt = ".tap"
                    case "AXA":
                        toAXA(Gpath)
                        GoutputExt = ".MPF"
            case "FELLER":
                match GoutputType:
                    case "HASS":
                        toHass(Gpath)
                        GoutputExt = ".tap"
                    case "AXA":
                        toAXA(Gpath)
                        GoutputExt = ".MPF"
            case "AXA":
                match GoutputType:
                    case "HASS":
                        toHass(Gpath)
                        GoutputExt = ".tap"
                    case "FELLER":
                        toFeller(Gpath)
                        GoutputExt = ".tap"

    

    #preview
    #if in line  "N1 G71" or "N1 G21"  add line to  preview
    preview.append(f"<p style='margin:0;padding:0;color: #ffba7a;'>Po konwercie: {GoutputType}</p>")
    searchItems= ["G71", "G21", "M02", "M30", "N7 G01 G43 G58", "N7 G01 G43 G54", "N7 G01 G54 G64"]
    searchStrategy = "highlight"
    with open(Gpath, "r") as file:
        for line in file:
            regex = re.compile("(%s)" % "|".join(map(re.escape, searchItems)))
            if regex.search(line):
                # preview.append(line)
                if searchStrategy == "highlight":
                    #if searchItems in line dont add same line
                    for item in searchItems:
                        if item in line:
                            if line in preview.toPlainText():
                                continue
                            else:
                                preview.append(blueText(item))
        preview.append(blueText(GoutputExt))

        
                   
                    
                            

                                

                        

    #done popup
    msg = QMessageBox()
    msg.setWindowTitle("Zakończono!")
    msg.setText("Konwertowanie zakończone!")
    msg.setIcon(QMessageBox.Information)
    msg.exec_()
    return
     


App = QApplication(sys.argv)

#window
window = QWidget()
window.setGeometry(100, 100, 800, 600)
window.setStyleSheet("background-color: #2b2b2b; color: #ffffff;")
window.setWindowTitle('Feller AXA Hass CNC Program Converter')
centerPoint = qt.QtWidgets.QDesktopWidget().availableGeometry().center()
window.move(centerPoint.x() - 400, centerPoint.y() - 300)

#variables
Gpath = ""
GinputType = ""
GoutputType = ""
GinputExt = ""
GoutputExt = ""

#labels
title = qt.QtWidgets.QLabel(window)
title.setFont(qt.QtGui.QFont('Arial', 15))
title.setText("Feller AXA Hass CNC Program Converter")
title.setStyleSheet("color: #ffba7a; font-weight: bold; text-align: center; width: 100%;")
title.move(160, 25)

#select file button
btnSelect = qt.QtWidgets.QPushButton('Wybierz Plik', window)
btnSelect.move(20, 60)
btnSelect.clicked.connect(selectFile)
btnSelect.setFont(qt.QtGui.QFont('Arial', 10))
btnSelect.setFixedWidth(120)
btnSelect.setFixedHeight(80)
btnSelect.setStyleSheet("QPushButton {background-color: #2b2b2b; color: #fff; font-weight: bold; outline: none; border: 1px solid #ffba7a; padding: 5px;} QPushButton::hover{background-color: #ffba7a; color: #2b2b2b; border:none; font-weight: bold; } ")

#convert button
btnConvert = qt.QtWidgets.QPushButton('Konwertuj', window)
btnConvert.move(20, 160)
btnConvert.setFont(qt.QtGui.QFont('Arial', 10))
btnConvert.setStyleSheet("QPushButton {background-color: #2b2b2b; color: #fff; font-weight: bold; outline: none; border: 2px solid #52fffc; padding: 5px;} QPushButton::hover{background-color: #52fffc; color: #2b2b2b; border:none; font-weight: bold; } ")
btnConvert.setFixedWidth(120)
btnConvert.clicked.connect(lambda: convert(GinputType))

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
cncType.setStyleSheet("color: #ffba7a; font-weight: bold;")

#line
hr = qt.QtWidgets.QFrame(window)
hr.setGeometry(0, 150, 800, 2)
hr.setStyleSheet("background-color: #ffffff; width: 100%;")
hr.setFrameShape(qt.QtWidgets.QFrame.HLine)
hr.setFrameShadow(qt.QtWidgets.QFrame.Sunken)

#label for CNC Type Pick
cncTypePickLabel = qt.QtWidgets.QLabel(window)
cncTypePickLabel.setFont(qt.QtGui.QFont('Arial', 10))
cncTypePickLabel.setText("Zmnień na Typ:")
cncTypePickLabel.move(160, 165)

#CNC Type Pick
cncTypePick = qt.QtWidgets.QComboBox(window)
font = qt.QtGui.QFont('Arial', 10)
font.setPointSize(10)
cncTypePick.setFont(font)
cncTypePick.setStyleSheet("QComboBox {color: #fff; background-color: #2b2b2b; border: 1px solid #ffba7a; padding: 5px; font-weight: bold; outline: none;} QComboBox::hover{background-color: #ffba7a; color: #2b2b2b; border:none; font-weight: bold; } ")
cncTypePick.move(280, 160)
cncTypePick.setFixedWidth(200)
cncTypePick.setFixedHeight(30)

#editlog window
editLog = qt.QtWidgets.QTextEdit(window)
editLog.setFont(font)
editLog.setStyleSheet("QTextEdit {color: #ffba7a;}")
editLog.setReadOnly(True)
editLog.setLineWrapMode(qt.QtWidgets.QTextEdit.NoWrap)
editLog.move(330, 220)
editLog.setFixedWidth(460)
editLog.setFixedHeight(360)
editLog.setStyleSheet("border: 2px solid #ffba7a; color: #fff; font-weight: bold; text-align: center; width: 100%;")

#label for editlog
editLogLabel = qt.QtWidgets.QLabel(window)
editLogLabel.setFont(qt.QtGui.QFont('Arial', 10))
editLogLabel.setText("Dniennik zmian:")
editLogLabel.setStyleSheet("color: #ffba7a; font-weight: bold; text-align: center; width: 100%;")
editLogLabel.move(330, 200)

#textedit for preview
preview = qt.QtWidgets.QTextEdit(window)
preview.setReadOnly(True)
preview.setFont(qt.QtGui.QFont('Arial', 10))
preview.move(20, 220)
preview.setStyleSheet("border: 2px solid #52fffc; color: #fff; font-weight: bold; text-align: center; width: 100%;")
preview.setFixedWidth(300)
preview.setFixedHeight(360)

#label for preview
previewLabel = qt.QtWidgets.QLabel(window)
previewLabel.setFont(qt.QtGui.QFont('Arial', 10))
previewLabel.setText("Podgląd:")
previewLabel.move(20, 200)
previewLabel.setStyleSheet("color: #52fffc; font-weight: bold; ")

window.show()
App.exec_()