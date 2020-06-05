import sys
import os
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox
from S2 import S2


class Control:
    def __init__(self):
        self.dirname = ""

    @classmethod
    def createInstances(cls):
        items = os.listdir(Control.dirname)
        print("Number of files: " + str(len(items)))
        for item in items:
            if item.endswith(".SAFE"):
                if item.startswith("S2"):
                    S2_image = S2(item)
                    S2.getMetaDataFile(S2_image)

    @classmethod
    def deleteInstances(cls):
        S2.images = []

    @classmethod
    def showInstances(cls, this):
        for image in this.images:
            values = image.__dict__
            print(values)

    @classmethod
    def getImage(cls, this):
        for image in this.images:
            this.getMetaDataFile(image)

    @staticmethod
    def errorMessage(message):
        win = QMessageBox()
        win.setWindowTitle("Error")
        win.setText(message)
        win.setIcon(QMessageBox.Critical)
        win.exec_()

    @staticmethod
    def infoMessage(message):
        win = QMessageBox()
        win.setWindowTitle("Information")
        win.setText(message)
        win.setIcon(QMessageBox.Information)
        win.exec_()

    @staticmethod
    def questionBox():
        win = QMessageBox()
        win.setWindowTitle("Input value")
        win.setText("Please write a specific name or a note for the selected area.  \n\n\n")
        input_name = QtWidgets.QLineEdit(win)
        input_name.setGeometry(50, 40, 200, 30)
        win.setStandardButtons(QMessageBox.Save | QMessageBox.Cancel)
        value = win.exec_()

        if value == QMessageBox.Cancel:
            return [True, ""]
        else:
            return [False, input_name.text()]

    @classmethod
    def closeWindow(cls, old, new):
        old.close()
        old.open = new
        old.open.show()
