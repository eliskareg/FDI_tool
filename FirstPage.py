import os
import sys
import io
from Page import Page
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QApplication, QMainWindow
from S2 import S2
from Control import Control
from SecondPage import SecondPage


class FirstPage(Page):

    def __init__(self):
        super().__init__()
        self.data_in_table = False
        self.setFixedSize(self.size())
        self.setupUi()

    def setupUi(self):
        about = self.menubar.addAction("About")
        about.triggered.connect(self.infoAbout)

        self.lineEdit = QtWidgets.QLineEdit(self)
        self.lineEdit.setGeometry(QtCore.QRect(70, 125, 360, 20))
        self.lineEdit.setObjectName("lineEdit")

        self.Browse = QtWidgets.QPushButton(self)
        self.Browse.setGeometry(QtCore.QRect(484, 120, 80, 30))
        self.Browse.setText("Browse")
        self.Browse.setObjectName("Browse")
        self.Browse.clicked.connect(self.browseDirs)

        self.Load = QtWidgets.QPushButton(self)
        self.Load.setGeometry(QtCore.QRect(590, 120, 80, 30))
        self.Load.setText("Load")
        self.Load.setObjectName("Load")
        self.Load.clicked.connect(self.loadClicked)

        self.OK = QtWidgets.QPushButton(self)
        self.OK.setGeometry(QtCore.QRect(650, 480, 80, 30))
        self.OK.setText("OK")
        self.OK.setObjectName("OK")
        self.OK.clicked.connect(self.okClicked)

        self.scrollArea = QtWidgets.QScrollArea(self)
        self.scrollArea.setGeometry(QtCore.QRect(20, 170, 761, 271))
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")

        self.scrollAreaWidgetContents = QtWidgets.QWidget()
        self.scrollAreaWidgetContents.setGeometry(QtCore.QRect(0, 0, 759, 269))
        self.scrollAreaWidgetContents.setObjectName("scrollAreaWidgetContents")

        self.scrollArea.setWidget(self.scrollAreaWidgetContents)

        self.tableWidget = QtWidgets.QTableWidget(self.scrollAreaWidgetContents)
        self.tableWidget.setGeometry(QtCore.QRect(10, 10, 741, 241))
        self.tableWidget.setColumnCount(11)
        self.tableWidget.setObjectName("tableWidget")

        self.tableWidget.setHorizontalHeaderItem(0, QtWidgets.QTableWidgetItem("Satellite"))
        self.tableWidget.setHorizontalHeaderItem(1, QtWidgets.QTableWidgetItem("Tile ID"))
        self.tableWidget.setHorizontalHeaderItem(2, QtWidgets.QTableWidgetItem("Date"))
        self.tableWidget.setHorizontalHeaderItem(3, QtWidgets.QTableWidgetItem("Time"))
        self.tableWidget.setHorizontalHeaderItem(4, QtWidgets.QTableWidgetItem("Cloud cover (%)"))
        self.tableWidget.setHorizontalHeaderItem(5, QtWidgets.QTableWidgetItem("Processing level"))
        self.tableWidget.setHorizontalHeaderItem(6, QtWidgets.QTableWidgetItem("NDVI"))
        self.tableWidget.setHorizontalHeaderItem(7, QtWidgets.QTableWidgetItem("RSR"))
        self.tableWidget.setHorizontalHeaderItem(8, QtWidgets.QTableWidgetItem("RVSI"))
        self.tableWidget.setHorizontalHeaderItem(9, QtWidgets.QTableWidgetItem("REIP"))
        self.tableWidget.setHorizontalHeaderItem(10, QtWidgets.QTableWidgetItem("Area"))

        self.label = QtWidgets.QLabel(self)
        self.label.setGeometry(QtCore.QRect(100, 480, 500, 30))
        self.label.setText("Please wait until the calculation is complete. This may "
                                                         "take several minutes...")
        self.label.setObjectName("label")

    def browseDirs(self):
        if self.lineEdit.text() == "":
            dirname = QtWidgets.QFileDialog.getExistingDirectory(self, "Select data directory", QtCore.QDir.rootPath())
            dirname = QtCore.QDir.toNativeSeparators(dirname)
            if os.path.isdir(dirname):
                self.lineEdit.setText(dirname)
                Control.dirname = dirname
                S2.dirname = dirname
        else:
            self.lineEdit.setText("")
            Control.deleteInstances()
            self.data_in_table = False
            self.browseDirs()

    def loadClicked(self):
        if not self.data_in_table:
            if self.lineEdit.text() == "":
                Control.errorMessage("Please insert your data directory path.")
                return
            else:
                Control.createInstances()
            if len(S2.images) == 0:
                Control.errorMessage("No satellite images of Sentinel 2 were found.")
            else:
                self.data_in_table = True
            self.createTable()
        else:
            Control.infoMessage("Data from the input directory have already been loaded.")

    def defineArea(self):
        shapefile = QtWidgets.QFileDialog.getOpenFileName(self, "Select SHP format", QtCore.QDir.rootPath(), "*.shp")
        return shapefile[0]

    def createTable(self):
        num_rows = len(S2.images)
        self.tableWidget.setRowCount(num_rows)
        for x in range(0, num_rows):
            self.tableWidget.setVerticalHeaderItem(x, QtWidgets.QTableWidgetItem())
            for y in range(0, 11):
                if y < 6:
                    attr = self.switch_cols(y)
                    self.tableWidget.setItem(x, y, QtWidgets.QTableWidgetItem(getattr(S2.images[x], attr)))
                elif y == 10:
                    input_shp = QtWidgets.QTableWidgetItem()
                    input_shp.setFlags(QtCore.Qt.ItemIsSelectable)
                    self.tableWidget.setItem(x, y, input_shp)
                else:
                    checkbox = QtWidgets.QTableWidgetItem()
                    checkbox.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
                    checkbox.setCheckState(QtCore.Qt.Unchecked)
                    self.tableWidget.setItem(x, y, checkbox)
        self.tableWidget.resizeColumnsToContents()
        self.tableWidget.itemClicked.connect(self.handleItemClicked)

    def handleItemClicked(self, item):
        col = item.column()
        if 5 < col < 10:
            attr = self.switch_VI(col)
            if item.checkState() == QtCore.Qt.Checked:
                setattr(S2.images[item.row()], attr, True)
            else:
                setattr(S2.images[item.row()], attr, False)
        elif col == 10:
            shp_path = self.defineArea()
            if shp_path != "":
                item.setText(shp_path)
                setattr(S2.images[item.row()], "shp_path", shp_path)
        self.tableWidget.resizeColumnsToContents()

    def okClicked(self):
        if self.data_in_table == False:
            Control.errorMessage("Please upload satellite imagery from your data folder.")
            return

        self.OK.setCursor(QtGui.QCursor(QtCore.Qt.BusyCursor))
        attrs = ["ndvi", "rsr", "rvsi", "reip"]
        attrs_values = []
        for image in S2.images:
            for attr in attrs:
                attrs_values.append(getattr(image, attr))
        if True not in attrs_values:
            Control.errorMessage("Please select at least one vegetation index to calculate.")
        else:
            self.getResults()
            Control.closeWindow(self, SecondPage())

    @staticmethod
    def getResults():
        stdout = sys.stdout
        sys.stdout = io.StringIO()
        # get printed values of this part of code:
        if S2.createOutDir():
            for image in S2.images:
                S2.getBands(image)
                S2.countValues(image)

        # restore sys.stdout
        output = sys.stdout.getvalue()
        sys.stdout = stdout

        results = open(Control.dirname + "/Output_data/ResultMessage.txt", "w")
        results.write(output)
        results.close()

    @staticmethod
    def switch_cols(col):
        switch = {
            0: "satellite",
            1: "tile_id",
            2: "date",
            3: "time",
            4: "cloud_cover",
            5: "processing_level"
        }
        return switch.get(col)

    @staticmethod
    def switch_VI(col):
        switch = {
            6: "ndvi",
            7: "rsr",
            8: "rvsi",
            9: "reip"
        }
        return switch.get(col)