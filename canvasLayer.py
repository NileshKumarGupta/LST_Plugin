from qgis.PyQt.QtGui import *
from qgis.PyQt.QtWidgets import *
from qgis.PyQt.QtCore import *
from qgis.gui import *
from qgis.core import QgsRasterLayer

from . import vectorprocessor, fileio


class CanvasLayer(QMainWindow):
    def __init__(self, form, lstLayer, folder):
        super(QMainWindow, self).__init__()
        self.lstLayer = lstLayer
        self.canvas = QgsMapCanvas()
        self.toolbar = self.addToolBar("Canvas actions")
        self.setFixedHeight(700)
        self.canvas.polygonList = list()
        self.form = form
        self.folder = folder

        # layout of the widget

        self.widget = QWidget()
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.canvas)

        # layout for showing the processed data
        self.tableLayout = QVBoxLayout()

        # scroll area for filling classes
        self.scrollArea = QScrollArea()
        self.scrollArea.setFixedHeight(200)
        self.layout.addWidget(self.scrollArea)

        # go button
        self.goButton = QPushButton("GO")
        self.goButton.clicked.connect(lambda: self.goFunc(self.canvas.polygonList))
        self.layout.addWidget(self.goButton)

        # Basic canvas settings
        self.canvas.setCanvasColor(Qt.white)
        self.canvas.setLayers([self.lstLayer])
        self.canvas.setExtent(self.lstLayer.extent())
        self.canvas.enableAntiAliasing(True)

        self.actionZoomIn = QAction("Zoom in", self)
        self.actionZoomOut = QAction("Zoom out", self)
        self.actionPan = QAction("Pan", self)

        self.actionZoomIn.setCheckable(True)
        self.actionZoomOut.setCheckable(True)
        self.actionPan.setCheckable(True)

        # create the map tools
        self.toolPan = QgsMapToolPan(self.canvas)
        self.toolPan.setAction(self.actionPan)
        self.toolZoomIn = QgsMapToolZoom(self.canvas, False)  # false = in
        self.toolZoomIn.setAction(self.actionZoomIn)
        self.toolZoomOut = QgsMapToolZoom(self.canvas, True)  # true = out
        self.toolZoomOut.setAction(self.actionZoomOut)

        self.actionZoomIn.triggered.connect(
            lambda: self.canvas.setMapTool(self.toolZoomIn)
        )
        self.actionZoomOut.triggered.connect(
            lambda: self.canvas.setMapTool(self.toolZoomOut)
        )
        self.actionPan.triggered.connect(lambda: self.canvas.setMapTool(self.toolPan))

        self.toolbar.addAction(self.actionZoomIn)
        self.toolbar.addAction(self.actionZoomOut)
        self.toolbar.addAction(self.actionPan)

        # basic settings end
        # add Polygon Select

        self.toolPolygon = PolygonMapTool(self.canvas, self.scrollArea)
        self.actionPolygonSelect = QAction("Polygon Select", self)
        self.actionPolygonSelect.triggered.connect(
            lambda: self.canvas.setMapTool(self.toolPolygon)
        )
        self.toolbar.addAction(self.actionPolygonSelect)
        self.toolPolygon.setAction(self.actionPolygonSelect)

        # add Undo
        self.actionUndo = QAction("Undo", self)
        self.toolbar.addAction(self.actionUndo)
        self.actionUndo.triggered.connect(
            lambda: self.removeLast(self.canvas.polygonList)
        )

        # self.canvas.setMapTool(self.toolPan)

        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)

    def goFunc(self, polygonList):
        classdict = dict()
        for entry in polygonList:
            if entry[3].currentText() == "":
                classdict["general".lower()] = list()
            else:
                classdict[entry[3].currentText().lower()] = list()

        for entry in polygonList:
            if entry[3].currentText() == "":
                classdict["general".lower()].append(entry[0])
            else:
                classdict[entry[3].currentText().lower()].append(entry[0])

        vproc = vectorprocessor.groupStats()
        stats = vproc.processAll(self.form, classdict, self.lstLayer, self.folder)
        print(stats)

        # add table to tableLayout
        tableWidget = QTableWidget()
        tableWidget.setColumnCount(3)
        tableWidget.setRowCount(len(stats) + 1)

        # set headings
        tableWidget.setItem(0, 0, QTableWidgetItem("Classes"))
        tableWidget.setItem(0, 1, QTableWidgetItem("Mean"))
        tableWidget.setItem(0, 2, QTableWidgetItem("Standard Deviation"))

        rownum = 1
        # add all entries
        for key in stats:
            tableWidget.setItem(rownum, 0, QTableWidgetItem(key))
            tableWidget.setItem(
                rownum, 1, QTableWidgetItem(str(round(stats[key][0], 2)))
            )
            tableWidget.setItem(
                rownum, 2, QTableWidgetItem(str(round(stats[key][1], 2)))
            )
            rownum += 1

        # add to layout
        self.tableLayout.addWidget(tableWidget)
        self.finalWidget = QWidget()
        self.finalWidget.setLayout(self.tableLayout)
        self.setCentralWidget(self.finalWidget)
        self.toolbar.hide()

    def removeLast(self, polygonList):
        if not len(polygonList):
            return
        removedEntry = polygonList.pop()
        removedEntry[1].hide()
        removedEntry[2].hide()
        removedEntry[4].hide()

        # to modify so as to remove current drawing


class PolygonMapTool(QgsMapToolEmitPoint):
    def __init__(self, canvas, scrollArea):
        super(QgsMapToolEmitPoint, self).__init__(canvas)
        self.canvas = canvas
        self.scrollArea = scrollArea

        self.rubberBand = QgsRubberBand(self.canvas, True)
        self.rubberBand.setColor(Qt.red)
        self.rubberBand.setWidth(2)
        self.pointList = list()
        self.polygonCount = 1
        self.templayout = QVBoxLayout()
        self.vertex = QgsVertexMarker(self.canvas)
        self.preClasses = ["Water Body", "Land Body"]
        self.lastDropDown = None

    def canvasDoubleClickEvent(self, e):
        point = self.toMapCoordinates(e.pos())

        print(point)
        self.pointList.append(point)
        if len(self.pointList) == 1:
            self.vertex = QgsVertexMarker(self.canvas)
            self.vertex.setCenter(point)
            self.vertex.setColor(Qt.red)
            self.vertex.setIconType(QgsVertexMarker.ICON_CIRCLE)

            QToolTip.setFont(QFont("SansSerif", 12))
            self.vertex.setToolTip("Area " + str(self.polygonCount))
            self.vertex.show()

            self.rubberBand.addPoint(point, False)
        else:
            self.rubberBand.addPoint(point, True)

    def keyPressEvent(self, e):
        enterKey = 16777220
        if not e.key() == enterKey or len(self.pointList) == 0:
            return
        self.rubberBand.addPoint(self.pointList[0], True)
        self.rubberBand.show()

        cWidget, editClass = self.fillClass()
        self.canvas.polygonList.append(
            (self.pointList, self.rubberBand, cWidget, editClass, self.vertex)
        )
        self.pointList = list()

        # to make different rubberbands

        self.rubberBand = QgsRubberBand(self.canvas, True)
        self.rubberBand.setColor(Qt.red)
        self.rubberBand.setWidth(2)

    def fillClass(self):
        cWidget = QWidget()

        hlayout = QHBoxLayout()
        labelArea = QLabel("Area " + str(self.polygonCount))
        self.polygonCount += 1
        labelClass = QLabel("   Class : ")

        dropDown = QComboBox()
        if self.lastDropDown:
            print(self.lastDropDown.currentText())
            if not self.preClasses.__contains__(self.lastDropDown.currentText()):
                self.preClasses.append(self.lastDropDown.currentText())

        for item in self.preClasses:
            dropDown.addItem(item)
        dropDown.addItem("Add New Class")

        dropDown.setFixedWidth(100)

        # dropDown.setEditable(True)
        dropDown.activated.connect(lambda index: self.addNew(index, dropDown))

        self.lastDropDown = dropDown
        # set fixed width
        # remove new class item

        hlayout.addWidget(labelArea)
        hlayout.addWidget(labelClass)
        hlayout.addWidget(dropDown)

        cWidget.setMinimumHeight(40)
        cWidget.setLayout(hlayout)

        # self.parentLayout.addWidget(cWidget)

        self.templayout.addWidget(cWidget)
        templistwidget = QWidget()
        templistwidget.setLayout(self.templayout)
        self.scrollArea.setWidget(templistwidget)

        return cWidget, dropDown

    def addNew(self, index, dropDown):
        if index == dropDown.count() - 1:
            dropDown.setEditable(True)
            dropDown.setItemText(index, "")
        else:
            dropDown.setEditable(False)
