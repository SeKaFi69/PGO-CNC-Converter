#feller axa hass CNC program converter

import sys
import os
import PyQt5 as qt
from PyQt5.QtWidgets import QApplication, QWidget, QFileDialog, QMessageBox
import re
import functions as f

#functions
def Text(text):
    return f"<p style='margin:0;padding:0;'>{text}</p>"
def blueText(text):
    return f"<p style='color: #52fffc; margin: 0; padding: 0;'>{text}</p>"
def errorText(text):
    return f"<p style='color: #ff0000; margin: 0; padding: 0;'>{text}</p>"
def orangeText(text):
    return f"<p style='color: #ffba7a; margin: 0; padding: 0;'>{text}</p>"
def greenText(text):
    return f"<p style='color: #33ff88; margin: 0; padding: 0;'>{text}</p>"

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
    global GinputType
    global Gsource
    preview.clear()

    editLog.append("Wybieranie pliku...")
    if Gsource:
        file, check = QFileDialog.getOpenFileName(None, "Wybierz plik z programem", Gsource, "CNC(*.tap *.MPF)")
    else:
        file, check = QFileDialog.getOpenFileName(None, "Wybierz plik z programem", "", "CNC(*.tap *.MPF)")
    if check:
        editLog.clear()
        cncTypePick.clear()
        fileExt = os.path.splitext(file)[1]
        global GfileExt
        GfileExt = fileExt

        Gsource = os.path.dirname(file)

        appendData(file, fileExt)
        recognizeFile(file)
        editLog.append(blueText(f"Rozpoznano plik jako {GinputType}"))
        
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
                                    match item:
                                        case "G43 G54":
                                            GinputType = "FELLER"
                                        case "G43 G58":
                                            GinputType = "HASS"
                                        case "G54 G64":
                                            GinputType = "AXA"                        
        preview.append(GfileExt)
        preview.append("")   
        preview.append("")   

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

def selectDestination():
    #select folder in which file will be saved
    editLog.append("Wybieranie folderu docelowego...")
    folder = QFileDialog.getExistingDirectory(None, "Wybierz folder docelowy", "")
    if folder:
        editLog.append(orangeText(f"Folder docelowy: {folder}"))
        destinationLabel.setText(blueText(f"Zapisz w: {folder}"))
        global Gfolder
        Gfolder = folder
        
        with open("destination.txt", "w") as file3:

            msg = QMessageBox()
            msg.setWindowTitle("Zapisz folder docelowy")
            msg.setText("Czy chcesz zapisać folder docelowy?")
            msg.setIcon(QMessageBox.Question)
            msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msg.setDefaultButton(QMessageBox.Yes)
            msg.setEscapeButton(QMessageBox.No)
            x = msg.exec_()
            if x == QMessageBox.Yes:
                editLog.append("Zapisywanie folderu docelowego...")
                file3.write(folder)
                destinationLabel.setText(blueText(f"Zapisz w: {folder}"))
                editLog.append("Zapisano folder docelowy!")
                editLog.append(orangeText(f"Folder docelowy: {folder}"))

            elif x == QMessageBox.No:
                editLog.append("Anulowano zapisywanie folderu docelowego!")
                editLog.append(blueText(f"Folder docelowy: {folder}"))
                Gfolder = folder
                return

    else:
        editLog.append("Anulowanie wybierania!")
        Gfolder = folder
        return

def selectSource():
    if editLog.toPlainText() != "":
        editLog.append(Text(""))
    #select folder in which file will be saved
    editLog.append("Wybieranie folderu źródłowego...")
    folder = QFileDialog.getExistingDirectory(None, "Wybierz folder źródłowy", "")
    if folder:
        editLog.append(orangeText(f"Folder źródłowy: {folder}"))
        global Gsource
        Gsource = folder

        msg = QMessageBox()
        msg.setWindowTitle("Zapisz folder źródłowy")
        msg.setText("Czy chcesz zapisać folder źródłowy?")
        msg.setIcon(QMessageBox.Question)
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.Yes)
        msg.setEscapeButton(QMessageBox.No)
        x = msg.exec_()
        if x == QMessageBox.Yes:
            editLog.append("Zapisywanie folderu źródłowego...")
            with open("source.txt", "w") as file2:
                file2.write(folder)
            textSource.setText(f"Źródło: {folder}")

            editLog.append("Zapisano folder źródłowy!")
            editLog.append(Text(""))
        elif x == QMessageBox.No:
            editLog.append("Anulowano zapisywanie folderu źródłowego!")
            editLog.append(blueText(f"Folder źródłowy: {folder}"))
            Gsource = folder
            return

    else:
        editLog.append("Anulowanie wybierania!")
        return

def toHass(path):
    editLog.append(blueText("=-=-= Konwertowanie na HASS =-=-="))
    editLog.append(path)
    with open(path, "r") as file:
        filedata = file.read()
    # puste linie
    while "\n\n" in filedata:
        filedata = filedata.replace("\n\n", "\n")
    editLog.append(Text("Usunięto puste linie"))

    #przygotowanie pliku
    filedataSmall = filedata.split("N1 ")[0]
    
    #komentarze ()
    if ";" in filedataSmall:
        filedataSmall = filedataSmall.replace(";", "(")
        filedataSmall = filedataSmall.replace("\n", ")\n")

        editLog.append(Text("Zamieniono komentarze z ; na ()"))

        while "((" in filedataSmall:
            filedataSmall = filedataSmall.replace("((", "(")

    # zamien filedataSmall
    filedata = filedata.replace(filedata.split("N1 ")[0], filedataSmall)

    # konwersja G43 G58, G71, M30
    if "G54 G64" or "G43 G54" or "G21" or "M02" in filedata:
        filedata = filedata.replace("G54 G64", "G43 G58")
        filedata = filedata.replace("G43 G54", "G43 G58")
        filedata = filedata.replace("G21", "G71")
        filedata = filedata.replace("M02", "M30")
    editLog.append(blueText("> G43 G58"))
    editLog.append(blueText("> G71"))
    editLog.append(blueText("> M30"))

    

    # % na początku i końcu
    if "%" not in filedata:
        filedata = "%\n" + filedata + "\n%"
    editLog.append(Text("Dodano % na początku i końcu programu"))

    # nazwa pliku
    fileName = os.path.splitext(path)[0]

    if "(AXA)" in fileName:
        path = path.replace("(AXA)", "(HASS)")
    elif "(Feller)" in fileName:
        path = path.replace("(Feller)", "(HASS)")
    elif "(HASS)" not in fileName:
        path = path.replace(fileName, fileName + "(HASS)")
    
    editLog.append(Text("Dodano (HASS) do nazwy pliku"))

    # rozszerzenie .tap
    fileExt = os.path.splitext(path)[1]
    if fileExt == ".tap":
        editLog.append(Text("Rozszerzenie jest już .tap"))
    else:
        path = path.replace(fileExt, ".tap")
        editLog.append(Text("Zmieniono rozszerzenie na .tap"))

    # miejsce zapisu
    pathSplit = path.rsplit("/", 1)
    if Gfolder == "":
        pathSplit[0] = Gsource
    else:
        pathSplit[0] = Gfolder
    path = pathSplit[0] + "/" + pathSplit[1]
    
    global Gpath
    Gpath = path

    # zapis
    with open(path, "w") as file:
        file.write(filedata)
        editLog.append(greenText("Plik zmnieniony pomyślnie!"))
        editLog.append(orangeText(f"Zapisano w: {path}"))
    file.close()
    return path

def toFeller(path):
    editLog.append(blueText("=-=-= Konwertowanie na Feller =-=-="))
    editLog.append(path)
    with open(path, "r") as file:
        filedata = file.read()
    # puste linie
    while "\n\n" in filedata:
        filedata = filedata.replace("\n\n", "\n")
    editLog.append(Text("Usunięto puste linie"))

    #przygotowanie pliku
    filedataSmall = filedata.split("N1 ")[0]
    if ")" in filedataSmall:
        filedataSmall = filedataSmall.replace(";", "")
        
    
    #komentarze ()
    if ";" in filedataSmall:
        filedataSmall = filedataSmall.replace(";", "(")
        filedataSmall = filedataSmall.replace("\n", ")\n")

        editLog.append(Text("Zamieniono komentarze z ; na ()"))

        while "((" in filedataSmall:
            filedataSmall = filedataSmall.replace("((", "(")

    # zamien filedataSmall
    filedata = filedata.replace(filedata.split("N1 ")[0], filedataSmall)

    # konwersja G43 G54, G21, M02
    if "G54 G64" or "G43 G58" or "G71" or "M30" in filedata:
        filedata = filedata.replace("G54 G64", "G43 G54")
        filedata = filedata.replace("G43 G58", "G43 G54")
        filedata = filedata.replace("G71", "G21")
        filedata = filedata.replace("M30", "M02")
    editLog.append(blueText("> G43 G54"))
    editLog.append(blueText("> G21"))
    editLog.append(blueText("> M02"))

    

    # % na początku i końcu
    if "%" not in filedata:
        filedata = "%\n" + filedata + "\n%"
    editLog.append(Text("Dodano % na początku i końcu programu"))

    # nazwa pliku
    fileName = os.path.splitext(path)[0]

    if "(HASS)" in fileName:
        path = path.replace("(HASS)", "(Feller)")
    elif "(AXA)" in fileName:
        path = path.replace("(AXA)", "(Feller)")
    elif "(Feller)" not in fileName:
        path = path.replace(fileName, fileName + "(Feller)")

    editLog.append(Text("Dodano (Feller) do nazwy pliku"))

    # rozszerzenie .tap
    fileExt = os.path.splitext(path)[1]
    if fileExt == ".tap":
        editLog.append(Text("Rozszerzenie jest już .tap"))
    else:
        path = path.replace(fileExt, ".tap")
        editLog.append(Text("Zmieniono rozszerzenie na .tap"))
    
    # miejsce zapisu
    pathSplit = path.rsplit("/", 1)
    if Gfolder == "":
        pathSplit[0] = Gsource
    else:
        pathSplit[0] = Gfolder
    path = pathSplit[0] + "/" + pathSplit[1]

    global Gpath
    Gpath = path

    # zapis
    with open(path, "w") as file:
        file.write(filedata)
        editLog.append(greenText("Plik zmnieniony pomyślnie!"))
        editLog.append(orangeText(f"Zapisano w: {path}"))
    file.close()

    return path

def toAXA(path):
    editLog.append(blueText("=-=-= Konwertowanie na AXA =-=-="))
    editLog.append(path)
    with open(path, "r") as file:
        filedata = file.read()
    # puste linie
    while "\n\n" in filedata:
        filedata = filedata.replace("\n\n", "\n")
    editLog.append(Text("Usunięto puste linie"))

    #przygotowanie pliku
    filedataSmall = filedata.split("N1 ")[0]
    #komentarze ;
    filedataSmall = filedataSmall.replace("(", ";")

    filedataSmall = filedataSmall.replace(")", "")

    while ";;" in filedataSmall:
        filedataSmall = filedataSmall.replace(";;", ";")
    
    editLog.append(Text("Zamieniono komentarze z () na ;"))

    # początek programu
    for line in filedataSmall.splitlines():
        if line.startswith("O"):
            editLog.append(Text(f"Usunięto początku programu: {line}"))
            filedataSmall = filedataSmall.replace(f"{line}\n", "")
            break
    # zamien filedataSmall
    filedata = filedata.replace(filedata.split("N1 ")[0], filedataSmall)

    # konwersja G54 G64, G71, M02

    filedata = filedata.replace('G54 ', '')
    filedata = filedata.replace('G58 ', '')
    filedata = filedata.replace('G43', 'G54 G64')
    filedata = filedata.replace('G21', 'G71')
    filedata = filedata.replace('M02', 'M30')

    editLog.append(blueText("> G54 G64"))
    editLog.append(blueText("> G71"))
    editLog.append(blueText("> M30"))

    # usun % na początku i końcu
    if "%" in filedata:
        filedata = filedata.replace("%\n", "")
        filedata = filedata.replace("\n%", "")
    editLog.append(Text("Usunięto % na początku i końcu programu"))

    # nazwa pliku
    fileName = os.path.splitext(path)[0]

    if "(AXA)" in fileName:
        path = path.replace("(AXA)", "(AXA)")
    elif "(Feller)" in fileName:
        path = path.replace("(Feller)", "(AXA)")
    elif "(AXA)" not in fileName:
        path = path.replace(fileName, fileName + "(AXA)")

    editLog.append(Text("Dodano (AXA) do nazwy pliku"))

    # rozszerzenie .MPF
    fileExt = os.path.splitext(path)[1]
    if fileExt == ".MPF":
        editLog.append(Text("Rozszerzenie jest już .MPF"))
    else:
        path = path.replace(fileExt, ".MPF")
        editLog.append(Text("Zmieniono rozszerzenie na .MPF"))

    # miejsce zapisu
    pathSplit = path.rsplit("/", 1)
    if Gfolder == "":
        pathSplit[0] = Gsource
    else:
        pathSplit[0] = Gfolder
    path = pathSplit[0] + "/" + pathSplit[1]

    global Gpath
    Gpath = path      

    # zapis
    with open(path, "w") as file:
        file.write(filedata)
        editLog.append(greenText("Plik zmnieniony pomyślnie!"))
        editLog.append(orangeText(f"Zapisano w: {path}"))
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
        preview.append(orangeText(f"Po konwersji: {GoutputType}"))

        
        match GoutputType:
            case "FELLER":
                toFeller(Gpath)
                GoutputExt = ".tap"
                preview.append(blueText(f.feller[0]))
                preview.append(blueText(f.feller[1]))
                preview.append(blueText(f.feller[2]))
                preview.append(blueText(GoutputExt))
            case "AXA":
                toAXA(Gpath)
                GoutputExt = ".MPF"
                preview.append(blueText(f.axa[0]))
                preview.append(blueText(f.axa[1]))
                preview.append(blueText(f.axa[2]))
                preview.append(blueText(GoutputExt))
                
            case "HASS":
                toHass(Gpath)
                GoutputExt = ".tap"
                preview.append(blueText(f.hass[0]))
                preview.append(blueText(f.hass[1]))
                preview.append(blueText(f.hass[2]))
                preview.append(blueText(GoutputExt))
    preview.append("")

    editLog.append(Text(""))
    # potwierdzenie zakończenia
    msg = QMessageBox()
    msg.setWindowTitle("Zakończono!")
    msg.setIcon(QMessageBox.Information)

    msg.setText("Konwertowanie zakończone!")
    msg.setInformativeText("Otworzyć plik?")    
    msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    msg.setDefaultButton(QMessageBox.Yes)

    if msg.exec_() == QMessageBox.Yes:
        os.startfile(Gpath)
    else:
        return
    return
     
App = QApplication(sys.argv)

#window
window = QWidget()
window.setGeometry(100, 100, 1000, 700)
window.setStyleSheet("background-color: #2b2b2b; color: #ffffff;")
window.setWindowTitle('Feller AXA Hass CNC Program Converter')
centerPoint = qt.QtWidgets.QDesktopWidget().availableGeometry().center()
window.move(centerPoint.x() - 400, centerPoint.y() - 400)

#variables

#if destination.txt not empty

    
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
title.move(260, 25)

#select file button
btnSelect = qt.QtWidgets.QPushButton('Wybierz Plik', window)
btnSelect.move(20, 30)
btnSelect.clicked.connect(selectFile)
btnSelect.setFont(qt.QtGui.QFont('Arial', 10))
btnSelect.setFixedWidth(140)
btnSelect.setFixedHeight(30)
btnSelect.setStyleSheet("QPushButton {background-color: #2b2b2b; color: #fff; font-weight: bold; outline: none; border: 1px solid #ffba7a; padding: 5px;} QPushButton::hover{background-color: #ffba7a; color: #2b2b2b; border:none; font-weight: bold; } ")

#select source folder
btnSelectSource = qt.QtWidgets.QPushButton('Wybierz Folder', window)
btnSelectSource.move(20, 70)
btnSelectSource.clicked.connect(selectSource)
btnSelectSource.setFont(qt.QtGui.QFont('Arial', 10))
btnSelectSource.setFixedWidth(140)
btnSelectSource.setFixedHeight(30)
btnSelectSource.setStyleSheet("QPushButton {background-color: #2b2b2b; color: #fff; font-weight: bold; outline: none; border: 1px solid #ffba7a; padding: 5px;} QPushButton::hover{background-color: #ffba7a; color: #2b2b2b; border:none; font-weight: bold; } ")

# source folder label
textSource = qt.QtWidgets.QLabel(window)
textSource.setFont(qt.QtGui.QFont('Arial', 10))
textSource.setFixedWidth(820)
textSource.move(170, 60)
textSource.setStyleSheet("color: #52fffc; font-weight: bold; text-align: left; width: 100%;")
if os.path.isfile("source.txt"):
    Gsource = open("source.txt", "r").read()
    textSource.setText(f"Źródło: {Gsource}")
else:
    textSource.setText("Źródło:")
    Gsource = ""

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
textExt.setFixedWidth(820)
textExt.move(170, 120)

#display path of selected file
textPath = qt.QtWidgets.QLabel(window)
textPath.setFont(qt.QtGui.QFont('Arial', 10))
textPath.setFixedWidth(800)
textPath.move(170, 80)

#display CNC Type
cncType = qt.QtWidgets.QLabel(window)
cncType.setFont(qt.QtGui.QFont('Arial', 10))
cncType.setFixedWidth(800)
cncType.move(170, 100)
cncType.setStyleSheet("color: #ffba7a; font-weight: bold;")

#line
hr = qt.QtWidgets.QFrame(window)
hr.setGeometry(0, 150, 1000, 2)
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
cncTypePick.setFixedWidth(100)
cncTypePick.setFixedHeight(30)

#editlog window
editLog = qt.QtWidgets.QTextEdit(window)
editLog.setFont(font)
editLog.setStyleSheet("QTextEdit {color: #ffba7a;}")
editLog.setReadOnly(True)
editLog.move(330, 220)
editLog.setFixedWidth(660)
editLog.setFixedHeight(460)
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
preview.setFixedHeight(460)

#label for preview
previewLabel = qt.QtWidgets.QLabel(window)
previewLabel.setFont(qt.QtGui.QFont('Arial', 10))
previewLabel.setText("Podgląd:")
previewLabel.move(20, 200)
previewLabel.setStyleSheet("color: #52fffc; font-weight: bold; ")

#select where to save files
btnDestination = qt.QtWidgets.QPushButton('Wybierz Folder', window)
btnDestination.move(400, 160)
btnDestination.clicked.connect(selectDestination)
btnDestination.setFont(qt.QtGui.QFont('Arial', 10))
btnDestination.setFixedWidth(150)
btnDestination.setFixedHeight(30)
btnDestination.setStyleSheet("QPushButton {background-color: #2b2b2b; color: #fff; font-weight: bold; outline: none; border: 1px solid #ffba7a; padding: 5px;} QPushButton::hover{background-color: #ffba7a; color: #2b2b2b; border:none; font-weight: bold; } ")
btnDestination.show()

#label for destination
destinationLabel = qt.QtWidgets.QLabel(window)
destinationLabel.setFont(qt.QtGui.QFont('Arial', 10))
if os.path.isfile("destination.txt"):
    Gfolder = open("destination.txt", "r").read()
    destinationLabel.setText(f"Zapisz w: {Gfolder}")
else:
    destinationLabel.setText("Zapisz w:")
    Gfolder = Gsource
destinationLabel.setFixedWidth(400)
destinationLabel.setFixedHeight(50)
destinationLabel.setAlignment(qt.QtCore.Qt.AlignLeft)
destinationLabel.move(560, 160)
destinationLabel.setStyleSheet("color: #ffba7a; font-weight: bold;")
destinationLabel.setWordWrap(True)

window.show()
App.exec_()