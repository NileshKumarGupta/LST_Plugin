from qgis.PyQt.QtGui import *
from qgis.PyQt.QtWidgets import *
from qgis.PyQt.QtCore import *
from qgis.gui import *
from qgis.core import QgsRasterLayer


class CanvasLayer(QMainWindow):
    def __init__(self, lstLayer):
        super(QMainWindow, self).__init__()
        self.lstLayer = lstLayer
        self.canvas = QgsMapCanvas()
        self.toolbar = self.addToolBar("Canvas actions")
        self.setFixedHeight(700)
        self.canvas.polygonList = list()

        # layout of the widget

        self.widget = QWidget()
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.canvas)

        # scroll area for filling classes
        self.scrollArea = QScrollArea()
        self.scrollArea.setFixedHeight(200)

        self.listWidget = QWidget()
        self.listWidgetLayout = QVBoxLayout()
        self.listWidget.setLayout(self.listWidgetLayout)

        self.scrollArea.setWidget(self.listWidget)
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

        self.toolPolygon = PolygonMapTool(self.canvas, self.listWidgetLayout)
        self.actionPolygonSelect = QAction("Polygon Select", self)
        self.actionPolygonSelect.triggered.connect(
            lambda: self.canvas.setMapTool(self.toolPolygon)
        )
        self.toolbar.addAction(self.actionPolygonSelect)
        self.toolPolygon.setAction(self.actionPolygonSelect)

        # add Undo
        self.actionUndo = QAction("Undo", self)
        self.toolbar.addAction(self.actionUndo)
        self.actionUndo.triggered.connect(lambda: self.removeLast)

        # self.canvas.setMapTool(self.toolPan)

        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)

    def goFunc(self, polygonList):
        print(self.canvas.polygonList)

    def removeLast(self):
        pass


class PolygonMapTool(QgsMapToolEmitPoint):
    def __init__(self, canvas, parentLayout):
        super(QgsMapToolEmitPoint, self).__init__(canvas)
        self.canvas = canvas
        self.parentLayout = parentLayout

        QgsMapToolEmitPoint.__init__(self, self.canvas)

        self.rubberBand = QgsRubberBand(self.canvas, True)
        self.rubberBand.setColor(Qt.red)
        self.rubberBand.setWidth(2)
        self.pointList = list()

    def canvasDoubleClickEvent(self, e):
        point = self.toMapCoordinates(e.pos())
        print(point)
        self.pointList.append(point)
        if len(self.pointList) == 1:
            vertex = QgsVertexMarker(self.canvas)
            vertex.setCenter(point)
            vertex.setColor(Qt.red)
            vertex.show()
            self.rubberBand.addPoint(point, False)
        else:
            self.rubberBand.addPoint(point, True)
            # self.rubberBand.show()

    def keyPressEvent(self, e):
        enterKey = 16777220
        if not e.key() == enterKey or len(self.pointList) == 0:
            return
        self.rubberBand.addPoint(self.pointList[0], True)
        self.rubberBand.show()

        cWidget, editClass = self.fillClass()
        self.canvas.polygonList.append(
            (self.pointList, self.rubberBand, cWidget, editClass)
        )
        self.pointList = list()

        # to make different rubberbands

        self.rubberBand = QgsRubberBand(self.canvas, True)
        self.rubberBand.setColor(Qt.red)
        self.rubberBand.setWidth(2)

        self.fillClass()

    def fillClass(self):
        cWidget = QWidget()

        hlayout = QHBoxLayout()
        labelArea = QLabel("Area 1")
        labelClass = QLabel("   Class : ")
        editClass = QLineEdit("General")
        hlayout.addWidget(labelArea)
        hlayout.addWidget(labelClass)
        hlayout.addWidget(editClass)

        cWidget.setMinimumHeight(40)
        cWidget.setLayout(hlayout)

        self.parentLayout.addWidget(cWidget)

        return cWidget, editClass
