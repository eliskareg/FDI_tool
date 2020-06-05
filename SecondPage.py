import os, ast
import rasterio
import fiona
import fnmatch
import pyqtgraph
import rasterstats
from rasterstats import zonal_stats
from rasterio import warp, features, crs
from fiona import crs, transform
from Page import Page
from PyQt5 import QtCore, QtGui, QtWidgets
from S2 import S2
from Control import Control


class SecondPage(Page):

    def __init__(self):
        super().__init__()
        self.setupUi()
        self.img = pyqtgraph.ImageItem()
        self.data = []
        self.zss = []
        self.dates_sort = []
        self.resize(1080, 521)
        self.setFixedSize(self.size())
        self.roi_name = ""
        self.roi_id = 0
        self.first_link = 0
        self.nodes_zs = []
        self.roi_coords = []
        self.gj_loaded = ""

    def setupUi(self):
        self.graphicsLayout = pyqtgraph.GraphicsLayoutWidget(self)
        self.graphicsLayout.setGeometry(QtCore.QRect(0, 21, 1080, 500))
        export = self.graphicsLayout.sceneObj.contextMenu
        del export[:]

        layout = self.graphicsLayout.ci.layout
        layout.setColumnFixedWidth(0, 500)
        layout.setRowFixedHeight(0, 480)

        font = QtGui.QFont()
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)

        grey = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(150, 150, 150))
        brush.setStyle(QtCore.Qt.SolidPattern)
        grey.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)

        white = QtGui.QPalette()
        brush = QtGui.QBrush(QtGui.QColor(210, 210, 210))
        brush.setStyle(QtCore.Qt.SolidPattern)
        white.setBrush(QtGui.QPalette.Active, QtGui.QPalette.WindowText, brush)

        self.graphicsPlot = self.graphicsLayout.addPlot(row=0, col=0)
        self.graphicsPlot.setMenuEnabled(enableMenu=None)
        self.graphicsPlot.invertY()
        self.graphicsPlot.setAspectLocked()
        self.graphicsPlot.scene().sigMouseMoved.connect(self.mouseMoved)

        self.roi = pyqtgraph.PolyLineROI([[0, 0], [0, 50], [50, 50], [50, 0]], closed=True,
                                         pen=pyqtgraph.mkPen('b', width=2))
        self.roi.setZValue(10)

        self.histogram = pyqtgraph.HistogramLUTWidget(self.graphicsLayout)
        self.histogram.setGeometry(QtCore.QRect(510, 21, 150, 460))
        self.histogram.setObjectName("histogram")

        self.pixelValue = QtWidgets.QLabel(self)
        self.pixelValue.setGeometry(QtCore.QRect(0, 25, 510, 30))
        self.pixelValue.setObjectName("pixelValue")
        self.pixelValue.setStyleSheet("background-color: rgb(0, 0, 0); padding-left: 10px;")
        self.pixelValue.setFont(font)
        self.pixelValue.setPalette(white)

        self.plotWidget = PlotWidget(self.graphicsLayout)
        self.plotWidget.setGeometry(QtCore.QRect(670, 25, 350, 200))
        self.plotWidget.setObjectName("plotWidget")

        self.LoadGraph = QtWidgets.QPushButton(self)
        self.LoadGraph.setGeometry(QtCore.QRect(830, 250, 80, 25))
        self.LoadGraph.setText("Load Graph")
        self.LoadGraph.setObjectName("LoadGraph")
        self.LoadGraph.clicked.connect(self.getROICoords)

        self.minLabel = QtWidgets.QLabel(self.graphicsLayout)
        self.minLabel.setGeometry(QtCore.QRect(750, 270, 50, 10))
        self.minLabel.setPalette(grey)
        self.minLabel.setText("Min:")

        self.meanLabel = QtWidgets.QLabel(self.graphicsLayout)
        self.meanLabel.setGeometry(QtCore.QRect(750, 285, 50, 10))
        self.meanLabel.setPalette(grey)
        self.meanLabel.setText("Mean:")

        self.medianLabel = QtWidgets.QLabel(self.graphicsLayout)
        self.medianLabel.setGeometry(QtCore.QRect(750, 300, 50, 10))
        self.medianLabel.setPalette(grey)
        self.medianLabel.setText("Median:")

        self.stdLabel = QtWidgets.QLabel(self.graphicsLayout)
        self.stdLabel.setGeometry(QtCore.QRect(910, 270, 50, 10))
        self.stdLabel.setPalette(grey)
        self.stdLabel.setText("StDev:")

        self.maxLabel = QtWidgets.QLabel(self.graphicsLayout)
        self.maxLabel.setGeometry(QtCore.QRect(910, 285, 50, 10))
        self.maxLabel.setPalette(grey)
        self.maxLabel.setText("Max:")

        self.countLabel = QtWidgets.QLabel(self.graphicsLayout)
        self.countLabel.setGeometry(QtCore.QRect(910, 300, 50, 10))
        self.countLabel.setPalette(grey)
        self.countLabel.setText("Count:")

        self.minValue = QtWidgets.QLabel(self.graphicsLayout)
        self.minValue.setGeometry(QtCore.QRect(810, 270, 50, 10))
        self.minValue.setPalette(grey)
        self.minValue.setText("null")

        self.meanValue = QtWidgets.QLabel(self.graphicsLayout)
        self.meanValue.setGeometry(QtCore.QRect(810, 285, 50, 10))
        self.meanValue.setPalette(grey)
        self.meanValue.setText("null")

        self.medianValue = QtWidgets.QLabel(self.graphicsLayout)
        self.medianValue.setGeometry(QtCore.QRect(810, 300, 50, 10))
        self.medianValue.setPalette(grey)
        self.medianValue.setText("null")

        self.stdValue = QtWidgets.QLabel(self.graphicsLayout)
        self.stdValue.setGeometry(QtCore.QRect(970, 270, 50, 10))
        self.stdValue.setPalette(grey)
        self.stdValue.setText("null")

        self.maxValue = QtWidgets.QLabel(self.graphicsLayout)
        self.maxValue.setGeometry(QtCore.QRect(970, 285, 50, 10))
        self.maxValue.setPalette(grey)
        self.maxValue.setText("null")

        self.countValue = QtWidgets.QLabel(self.graphicsLayout)
        self.countValue.setGeometry(QtCore.QRect(970, 300, 50, 10))
        self.countValue.setPalette(grey)
        self.countValue.setText("null")

        self.linkLabel = QtWidgets.QLabel(self.graphicsLayout)
        self.linkLabel.setGeometry(QtCore.QRect(790, 320, 170, 20))
        self.linkLabel.setText("Show S2 image on sensing date of:")
        self.linkLabel.setPalette(white)

        self.prev = QtWidgets.QPushButton(self.graphicsLayout)
        self.prev.setGeometry(QtCore.QRect(690, 385, 20, 20))
        self.prev.setText("\u276e")
        self.prev.setFont(QtGui.QFont("Segoe UI", 8, 50))
        self.prev.clicked.connect(self.prevClicked)
        self.prev.hide()

        self.next = QtWidgets.QPushButton(self.graphicsLayout)
        self.next.setGeometry(QtCore.QRect(1010, 385, 20, 20))
        self.next.setText("\u276f")
        self.next.setFont(QtGui.QFont("Segoe UI", 8, 50))
        self.next.clicked.connect(self.nextClicked)
        self.next.hide()

        self.Export = QtWidgets.QToolButton(self)
        self.Export.setGeometry(QtCore.QRect(830, 470, 80, 25))
        self.Export.setText("Export")
        self.Export.setObjectName("Export")
        self.Export.setCheckable(True)
        self.Export.clicked.connect(self.exportClicked)

        self.selectVI = self.menubar.addMenu("Select VI")
        self.group = QtWidgets.QActionGroup(self.selectVI)

        loadROI = self.menubar.addAction("Load ROI")
        loadROI.triggered.connect(self.loadGeoJSON)

        about = self.menubar.addAction("About")
        about.triggered.connect(self.infoAbout)

        menu = self.defineArea()
        vis = list(menu.keys())

        for vi in vis:
            areas = menu[vi]
            self.vi_menu = self.selectVI.addMenu(vi)
            for area in areas:
                self.area_menu = QtWidgets.QAction(area, self)
                self.area_menu.setCheckable(True)
                self.area_menu.setParent(self.vi_menu)
                self.title = self.area_menu.parent().title()
                self.area_menu.parentWidget().setAccessibleName(vi)
                self.vi_menu.addAction(self.area_menu)
                self.group.addAction(self.area_menu)
        self.group.setExclusive(True)
        self.selectVI.triggered[QtWidgets.QAction].connect(self.actionVI)

    def defineArea(self):
        path = Control.dirname + "/Output_data/"
        areas = {}
        for path, sub_dirs, files in os.walk(path):
            for file in files:
                if fnmatch.fnmatch(file, "*.tiff"):
                    file_split = file.rsplit("_")
                    if len(file_split) > 5:
                        if len(file_split) > 6:
                            area = file_split[3] + "_" + file_split[4]
                        else:
                            area = file_split[3]
                    else:
                        area = file_split[2]
                    vi = ((file_split[-1]).split("."))[0]
                    areas.setdefault(vi, [])
                    if area not in areas[vi]:
                        areas[vi].append(area)
        return areas

    def actionVI(self, action):
        dates = []
        path = Control.dirname + "/Output_data/"
        for path, sub_dirs, files in os.walk(path):
            for file in files:
                self.plotWidget.y_label = action.parentWidget().title()
                if fnmatch.fnmatch(file, ("*" + action.text() + "*" + action.parentWidget().title() + ".tiff")):
                    file_split = file.rsplit("_")
                    if len(file_split) > 5:
                        date = file_split[2][0:8]
                    else:
                        date = file_split[1][0:8]
                    dates.append((int(date), file))
        dates_sort = sorted(dates, key=lambda x: x[0], reverse=True)
        self.createLinkButtons(dates_sort)
        self.openImage(0, dates_sort)

    def createLinkButtons(self, dates_sort):
        for i in range(len(dates_sort)):
            setattr(self, "linkButton" + str(i), QtWidgets.QCommandLinkButton(self.graphicsLayout))
            date = str(dates_sort[i][0])
            date_format = date[0:4] + "-" + date[4:6] + "-" + date[6:8]
            link = getattr(self, "linkButton" + str(i))
            link.clicked.connect(getattr(self, "connectLink")(i))
            link.setCheckable(True)
            link.setObjectName("linkButton")
            link.setText(date_format)
            link.setFont(QtGui.QFont("Segoe UI", 11, 50))
            link.setStyleSheet("color: rgb(10, 10, 255);")
            link.setChecked(False)
        self.setLinkButtonsHidden()
        self.drawLinkButtons(dates_sort)
        if len(dates_sort) >= 6:
            self.next.show()

    def connectLink(self, pos):
        return lambda: self.openImage(pos, self.dates_sort)

    def drawLinkButtons(self, dates_sort):
        num = self.first_link + 6
        geom = [(720, 345), (720, 375), (720, 405), (880, 345), (880, 375), (880, 405)]
        if len(dates_sort) < num:
            num = len(dates_sort)
        for i in range(self.first_link, num):
            link = getattr(self, "linkButton" + str(i))
            link.setGeometry(QtCore.QRect(geom[i - self.first_link][0], geom[i - self.first_link][1], 125, 30))
            link.show()

    def setLinkButtonsUnchecked(self):
        for i in range(len(self.dates_sort)):
            link = getattr(self, "linkButton" + str(i))
            link.setFont(QtGui.QFont("Segoe UI", 11, 50))
            link.setStyleSheet("color: rgb(10, 10, 255);")
            link.setChecked(False)

    def setLinkButtonsHidden(self):
        for i in range(len(self.dates_sort)):
            link = getattr(self, "linkButton" + str(i))
            link.hide()

    def nextClicked(self):
        if (len(self.dates_sort) - 6) >= 3:
            self.first_link += 3
        else:
            self.first_link += 3
            self.next.hide()
        self.prev.show()
        self.setLinkButtonsHidden()
        self.drawLinkButtons(self.dates_sort)

    def prevClicked(self):
        if (self.first_link - 3) > 0:
            self.first_link -= 3
        elif (self.first_link - 3) == 0:
            self.first_link -= 3
            self.prev.hide()
        self.next.show()
        self.setLinkButtonsHidden()
        self.drawLinkButtons(self.dates_sort)

    def openImage(self, pos, dates_sort):
        try:
            QtWidgets.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
            QtCore.QCoreApplication.addLibraryPath("/virtualenv/Lib/site-packages/PyQt5/Qt/plugins/imageformats")

            self.removeImageItem()
            self.setLinkButtonsUnchecked()
            link = getattr(self, "linkButton" + str(pos))
            link.setChecked(True)
            link.setFont(QtGui.QFont("Segoe UI", 11, 75))
            link.setStyleSheet("color: rgb(5, 30, 115);")
            self.showStatValues(pos)

            with rasterio.open(Control.dirname + "/Output_data/" + dates_sort[pos][1], "r+") as infile:
                r = infile.read()
                profile = infile.profile
                profile["dtype"] = rasterio.float32

                self.img = pyqtgraph.ImageItem(r[0].astype(rasterio.float32))
                self.img.setOpts(axisOrder="row-major")
                self.data = r[0]
                self.raster = infile
                self.graphicsPlot.addItem(self.img, autoHistogramRange=False)
                self.graphicsPlot.addItem(self.roi)
                if dates_sort != self.dates_sort:
                    self.getROICoords()
                    self.dates_sort = dates_sort
                self.histogram.setImageItem(self.img)
                self.setHistRange(dates_sort[pos][1][-9:-5])
                QtWidgets.QApplication.restoreOverrideCursor()

        except OSError:
            Control.errorMessage("Cannot load this image.")

    def mouseMoved(self, ev):
        if self.graphicsPlot.sceneBoundingRect().contains(ev) and self.img.image is not None:
            mousePoint = self.img.getViewBox().mapToItem(self.img, ev)
            if 0 <= mousePoint.x() <= len(self.data[0]) and 0 <= mousePoint.y() <= len(self.data):
                text = ""
                if self.data[int(mousePoint.y())][int(mousePoint.x() - 0.049)] == -999.0:
                    text = "Pixel value = null"
                else:
                    text = "Pixel value = %0.3f" % (self.data[int(mousePoint.y())][int(mousePoint.x() - 0.049)])
                self.pixelValue.setText(text)

    def getROICoords(self):
        self.zss = []
        hh = self.roi.getHandles()
        new_roi_coords = [self.roi.mapToItem(self.img, h.pos()) for h in hh]
        if new_roi_coords != self.roi_coords:
            self.gj_loaded = ""
            self.roi_coords = new_roi_coords
        self.createGeoJSONforZS()

    def createGeoJSONtoExport(self):
        if self.gj_loaded != "":
            return
        nodes_gj = [] # supported format to create geojson (epsg:4326)
        for point in self.roi_coords:
            xy = self.raster.xy(self.roi_coords[self.roi_coords.index(point)].y() - 0.5,
                                self.roi_coords[self.roi_coords.index(point)].x() -0.5)
            nodes_gj.append(xy[0])
            nodes_gj.append(xy[1])
        nodes_gj.append(nodes_gj[0])
        nodes_gj.append(nodes_gj[1])

        ys, xs = warp.transform(self.raster.crs, {'init': 'epsg:4326'}, nodes_gj[::2], nodes_gj[1::2])
        nodes_proj = []
        for i in range(0, len(ys)):
            nodes_proj.append([ys[i], xs[i]])
        geojson = """{"type": "FeatureCollection", "features": [{"type": "Feature", "properties": {}, "geometry":
                        {"type": "Polygon", "coordinates": [""" + str(nodes_proj) + """]}}]}"""

        if self.createGeoJSONDir():
            with open(Control.dirname + "/Output_data/GeoJSON/" + str(self.roi_id) + ".geojson", "w") as gj:
                gj.write(geojson)
                gj.close()

    def createGeoJSONforZS(self):
            self.nodes_zs = []  # supported format to count zonal statistics (epsg of input raster image)
            for point in self.roi_coords:
                xy = self.raster.xy(self.roi_coords[self.roi_coords.index(point)].y() - 0.5,
                                    self.roi_coords[self.roi_coords.index(point)].x() - 0.5)
                self.nodes_zs.append([xy[0], xy[1]])
            self.nodes_zs.append(self.nodes_zs[0])

            geojson_zs = """{"type": "FeatureCollection", "features": [{"type": "Feature", "properties": {}, "geometry":
                    {"type": "Polygon", "coordinates": [""" + str(self.nodes_zs) + """]}}]}"""
            self.countZonalStats(geojson_zs)

    def createGeoJSONDir(self):
        try:
            os.mkdir(Control.dirname + "/Output_data/GeoJSON")
            print("GeoJSON directory was created.")
            return True
        except OSError:
            if os.path.exists(Control.dirname + "/Output_data/GeoJSON"):
                gjs = os.listdir(Control.dirname + "/Output_data/GeoJSON")
                gjs_int = []
                for gj in gjs:
                    if gj.endswith(".geojson"):
                        gjs_int.append(gj.split(".")[0])
                gjs_int.sort(key=int, reverse=True)
                if len(gjs_int) != 0:
                    self.roi_id = int(gjs_int[0]) + 1

                print("GeoJSON directory already exists.")
                return True
            else:
                print("Creation of GeoJSON directory failed.")
                return False

    def countZonalStats(self, geojson):
        try:
            self.plotWidget.clearGraph()
            self.plotWidget.x = {}
            self.plotWidget.y = []
            dates = []
            names = []
            for i in self.dates_sort:
                date = str(i[0])
                date_format = date[0:4] + "-" + date[4:6] + "-" + date[6:8]
                dates.append("")
                dates.append(date_format)
                names.append(i[1])
            self.plotWidget.x = dict(enumerate(dates))

            id_zs = 1
            for name in names:
                with rasterio.open(Control.dirname + "/Output_data/" + name) as src:
                    affine = src.transform
                    r = src.read(1)
                    zs = zonal_stats(geojson, r, stats=["min", "mean", "median", "std", "max", "count"],
                                     affine=affine, nodata=-999, all_touched=True)
                    zs[0]['id'] = id_zs
                    zs[0]['date'] = dates[id_zs]
                    zs[0]['name'] = name
                    if zs[0]['mean'] is None:
                        self.plotWidget.y.append(0)
                        self.plotWidget.y.append(0)
                    else:
                        self.plotWidget.y.append(zs[0]['mean'])
                        self.plotWidget.y.append(zs[0]['mean'])
                    self.zss.append(zs[0])
                id_zs = id_zs + 2
            self.plotWidget.drawGraph()
            self.showStatValues(0)

        except OSError:
            Control.errorMessage("Cannot count raster statistics.")

    def exportClicked(self):
        canceled = Control.questionBox()
        self.roi_name = canceled[1]
        if canceled[0]:
            return

        try:
            self.getROICoords()
            self.createGeoJSONtoExport()

        except OSError:
            Control.errorMessage("GeoJSON cannot be created.")

        code = ""
        if self.gj_loaded != "":
            code = self.gj_loaded
        else:
            code = str(self.roi_id)
        gj = fiona.open(Control.dirname + "/Output_data/GeoJSON/" + code + ".geojson", "r")
        str_coords = ""
        for ft in gj:
            str_coords = "".join(str(i) for i in ft["geometry"]["coordinates"][0])

        content = "geometry;" + str_coords + ";\nindex;" + self.plotWidget.y_label \
                  + ";\narea;" + self.roi_name + ";\ngeojson;" + code + ";"
        stats = [["date", ""], ["min", ""], ["mean", ""], ["median", ""], ["max", ""], ["std", ""], ["count", ""]]
        for i in range(len(self.zss)):
            for j in range(len(stats)):
                if self.zss[i][stats[j][0]] is not None:
                    if i + 1 < len(self.zss):
                        if j == 0:
                            stats[j][1] += ";" + self.zss[i][stats[j][0]] + ";difference" + str(i + 1)
                        elif j == 6:
                            stats[j][1] += ";" + str(self.zss[i][stats[j][0]]) + ";0"
                        else:
                            stats[j][1] += ";"\
                                           + ("{:.3f}".format(round(self.zss[i][stats[j][0]], 3))).replace(".", ",")\
                                           + ";" + ("{:.3f}".format(round(self.zss[i][stats[j][0]]
                                                                          - self.zss[i + 1][stats[j][0]],
                                                                    3))).replace(".", ",")
                    else:
                        if j == 0:
                            stats[j][1] += ";" + self.zss[i][stats[j][0]]
                        elif j == 6:
                            stats[j][1] += ";" + str(self.zss[i][stats[j][0]])
                        else:
                            stats[j][1] += ";" + ("{:.3f}".format(self.zss[i][stats[j][0]])).replace(".", ",")
                else:
                    if i + 1 < len(self.zss):
                        stats[j][1] += ";null;null"
                    else:
                        stats[j][1] += ";null"

        for i in range(len(stats)):
            content += "\n" + stats[i][0] + stats[i][1]
        content += "\n\n\n"

        try:
            mode = "w"
            if os.path.isfile(Control.dirname + "/Output_data/export.csv"):
                mode = "a"

            csv = open(Control.dirname + "/Output_data/export.csv", mode)
            csv.write(content)
            csv.close()

            mode_c = "w"
            header_c = "id;geometry;\n"
            if os.path.isfile(Control.dirname + "/Output_data/GeoJSON/coords.csv"):
                mode_c = "a"
                header_c = ""
            csv_coords = open(Control.dirname + "/Output_data/GeoJSON/coords.csv", mode)
            csv_coords.write(header_c + str(self.roi_id) + ";" + str(self.nodes_zs) + ";\n")
            csv_coords.close()

            Control.infoMessage("Summary statistics was successfully exported.")

        except OSError:
            Control.errorMessage(
                "Cannot write to file 'export.csv'. Please close the file and try to export data again.")

    def setHistRange(self, vi):
        colors = [[0, 0, 0, 255], [80, 0, 255, 255], [220, 0, 0, 255], [250, 245, 30, 255], [40, 230, 40, 255],
                  [30, 150, 40, 255], [30, 150, 40, 255]]

        if vi == "NDVI":
            self.histogram.setLevels(-1, 1)
            self.histogram.setHistogramRange(-1.0, 1.0, 0.1)
            self.histogram.item.gradient.setColorMap(pyqtgraph.ColorMap([0.0, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0], colors))
        elif vi == "_RSR":
            self.histogram.setLevels(0, 20)
            self.histogram.setHistogramRange(0.0, 20.0, 0.1)
            self.histogram.item.gradient.setColorMap(pyqtgraph.ColorMap([0.0, 0.05, 0.15, 0.25, 0.6, 1.0], colors))
        elif vi == "RVSI":
            self.histogram.setLevels(-500, 2500)
            self.histogram.setHistogramRange(-500.0, 2500.0, 0.1)
            self.histogram.item.gradient.setColorMap(pyqtgraph.ColorMap([0.0, 0.2, 0.3, 0.4, 0.7, 1.0], colors))
        elif vi == "REIP":
            self.histogram.setLevels(680, 760)
            self.histogram.setHistogramRange(680.0, 760.0, 0.1)
            self.histogram.item.gradient.setColorMap(pyqtgraph.ColorMap([0.0, 0.35, 0.4, 0.45, 0.5, 0.55], colors))

    def removeImageItem(self):
        if self.img != pyqtgraph.ImageItem():
            self.graphicsPlot.removeItem(self.img)

        self.img = pyqtgraph.ImageItem()
        self.data = []

    def showStatValues(self, pos):
        if self.zss:
            stats = ["min", "mean", "median", "max", "std", "count"]
            for i in range(len(stats)):
                if self.zss[pos][stats[i]] is not None:
                    if i == 5:
                        getattr(self, stats[i] + "Value").setText(str(self.zss[pos][stats[i]]))
                    else:
                        getattr(self, stats[i] + "Value").setText("{:.3f}".format(self.zss[pos][stats[i]]))
                else:
                    getattr(self, stats[i] + "Value").setText("null")

    def loadGeoJSON(self):
        if len(self.data) > 0:
            geojson = QtWidgets.QFileDialog.getOpenFileName(self, "Select GeoJSON format", QtCore.QDir.rootPath(),
                                                            "*.geojson")
            self.gj_loaded = ((os.path.basename(geojson[0])).split("."))[0]
            if os.path.isfile(Control.dirname + "/Output_data/GeoJSON/coords.csv"):
                csv_coords = open(Control.dirname + "/Output_data/GeoJSON/coords.csv", "r")
            else:
                Control.errorMessage("Cannot find coords.csv table.")
                return

            lines = csv_coords.readlines()
            for line in lines:
                if line.startswith(self.gj_loaded + ";"):
                    line_str = line.split(";")[1]
                    coords = ast.literal_eval(line_str)
                    points = []
                    for coord in coords:
                        point = QtCore.QPoint(self.raster.index(coord[0], coord[1])[1],
                                              self.raster.index(coord[0], coord[1])[0])
                        points.append(point)
                    self.roi.setPoints(points, True)
                    self.roi_coords = points
            csv_coords.close()
        else:
            Control.errorMessage("No satellite image is loaded. Please select vegetation index and area to display.")


class PlotWidget(pyqtgraph.PlotWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.x = {}
        self.y = []
        self.y_label = ""
        self.plotItem.setMenuEnabled(False)
        self.plotItem.enableAutoRange(True)

    def updateGraph(self):
        self.setCursor(QtCore.Qt.BusyCursor)
        self.clearGraph()
        try:
            if self.x != {}:
                self.drawGraph()
            self.setCursor(QtCore.Qt.ArrowCursor)
        except OSError:
            Control.errorMessage("This graph cannot be loaded.")

    def drawGraph(self):
        if self.x != {} and self.y != []:
            self.x[len(self.y)] = ""
            self.plotItem.plot(list(self.x.keys()), self.y, stepMode=True, fillLevel=0, brush=(0, 0, 255, 150))
            self.plotItem.setLabel("left", self.y_label)
            self.plotItem.setLabel("bottom", "S2 images")
            y_axis = self.getPlotItem().getAxis("left")
            y_axis.setTicks([[(value, '{:.3f}'.format(value)) for value in self.y], []])
            x_axis = self.getPlotItem().getAxis("bottom")
            x_axis.setTicks([[v for v in list(self.x.items())]])
            self.autoRange(padding=0.05)

    def clearGraph(self):
        self.clear()
        return
