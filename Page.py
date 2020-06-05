from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow


class Page(QMainWindow):

    def __init__(self):
        super().__init__()
        self.resize(800, 600)
        self.setWindowTitle("FDI_tool")

        self.menubar = QtWidgets.QMenuBar(self)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 20))
        self.menubar.setObjectName("menubar")
        self.setMenuBar(self.menubar)

    def infoAbout(self):
        win = QtWidgets.QDialog(self)
        win.setWindowTitle("About")
        win.setGeometry(QtCore.QRect(300, 100, 600, 370))

        label = QtWidgets.QLabel(win)
        label.setGeometry(QtCore.QRect(75, 10, 450, 60))
        label.setLayoutDirection(QtCore.Qt.LeftToRight)
        label.setAlignment(QtCore.Qt.AlignCenter)
        label.setWordWrap(True)
        label.setObjectName("info")
        label.setText("FDI_tool is a tool for automatic identification of forest disturbances using Sentinel-2 "
                      "imagery. The tool was created as a part of the bachelor thesis.")

        tableWidget = QtWidgets.QTableWidget(win)
        tableWidget.setGeometry(QtCore.QRect(50, 70, 500, 250))
        tableWidget.setObjectName("tableView")
        tableWidget.setColumnCount(2)
        tableWidget.setRowCount(9)

        tableWidget.setHorizontalHeaderItem(0, QtWidgets.QTableWidgetItem(" "))
        tableWidget.setHorizontalHeaderItem(1, QtWidgets.QTableWidgetItem(" "))
        tableWidget.setVerticalHeaderItem(0, QtWidgets.QTableWidgetItem(" "))
        tableWidget.setVerticalHeaderItem(1, QtWidgets.QTableWidgetItem(" "))
        tableWidget.setVerticalHeaderItem(2, QtWidgets.QTableWidgetItem(" "))
        tableWidget.setVerticalHeaderItem(3, QtWidgets.QTableWidgetItem(" "))
        tableWidget.setVerticalHeaderItem(4, QtWidgets.QTableWidgetItem(" "))
        tableWidget.setVerticalHeaderItem(5, QtWidgets.QTableWidgetItem(" "))
        tableWidget.setVerticalHeaderItem(6, QtWidgets.QTableWidgetItem(" "))
        tableWidget.setVerticalHeaderItem(7, QtWidgets.QTableWidgetItem(" "))
        tableWidget.setVerticalHeaderItem(8, QtWidgets.QTableWidgetItem(" "))

        tableWidget.setItem(0, 0, QtWidgets.QTableWidgetItem("Author:"))
        tableWidget.setItem(1, 0, QtWidgets.QTableWidgetItem("Supervisor:"))
        tableWidget.setItem(2, 0, QtWidgets.QTableWidgetItem("Department: "))
        tableWidget.setItem(3, 0, QtWidgets.QTableWidgetItem("Faculty:"))
        tableWidget.setItem(4, 0, QtWidgets.QTableWidgetItem("University:"))
        tableWidget.setItem(5, 0, QtWidgets.QTableWidgetItem("Year:"))
        tableWidget.setSpan(6, 0, 2, 1)
        tableWidget.setItem(6, 0, QtWidgets.QTableWidgetItem("Bachelor thesis:"))
        tableWidget.setItem(7, 0, QtWidgets.QTableWidgetItem())
        tableWidget.setItem(8, 0, QtWidgets.QTableWidgetItem("Documentation:"))

        tableWidget.setItem(0, 1, QtWidgets.QTableWidgetItem("Eliška Regentová"))
        tableWidget.setItem(1, 1, QtWidgets.QTableWidgetItem("doc. RNDr. Vilém Pechanec, Ph.D."))
        tableWidget.setItem(2, 1, QtWidgets.QTableWidgetItem("Department of Geoinformatics"))
        tableWidget.setItem(3, 1, QtWidgets.QTableWidgetItem("Faculty of Science"))
        tableWidget.setItem(4, 1, QtWidgets.QTableWidgetItem("Palacký University, Olomouc"))
        tableWidget.setItem(5, 1, QtWidgets.QTableWidgetItem("2020"))
        tableWidget.setSpan(6, 1, 2, 1)
        tableWidget.setItem(6, 1, QtWidgets.QTableWidgetItem("Automation of Forest Disturbance Identification "
                                                             "based on Sentinel Data"))
        tableWidget.setItem(7, 1, QtWidgets.QTableWidgetItem(" "))
        tableWidget.setItem(8, 1, QtWidgets.QTableWidgetItem("Documentation (Czech only)"))
        tableWidget.resizeColumnsToContents()
        tableWidget.resizeRowsToContents()

        buttonBox = QtWidgets.QDialogButtonBox(win)
        buttonBox.setGeometry(QtCore.QRect(470, 330, 80, 30))
        buttonBox.setOrientation(QtCore.Qt.Horizontal)
        buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Ok)
        buttonBox.setObjectName("buttonBox")
        buttonBox.accepted.connect(lambda: self.closeInfo(win))

        win.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
        win.show()

    @staticmethod
    def closeInfo(win):
        win.accept()
        win.deleteLater()
