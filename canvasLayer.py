from qgis.PyQt.QtGui import *
from qgis.PyQt.QtWidgets import *
from qgis.PyQt.QtCore import *
from qgis.gui import *
from qgis.core import QgsRasterLayer

class polygonSelect(QgsMapTool):

    def __init__(self, canvas):

        QgsMapTool.__init__(self, canvas)
        self.canvas = canvas
    
    def canvasPressEvent(self, event):

        pass

class CanvasLayer(QMainWindow):
    def __init__(self, lstLayer):
        super(QMainWindow, self).__init__()
        self.lstLayer = lstLayer
        self.canvas = Canvas(self.lstLayer)
        self.toolbar = self.addToolBar("Canvas actions")
        self.setCentralWidget(self.canvas)

        # Basic canvas settings

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
        self.actionPan.triggered.connect(
            lambda: self.canvas.setMapTool(self.pan)
        )

        self.toolbar.addAction(self.actionZoomIn)
        self.toolbar.addAction(self.actionZoomOut)
        self.toolbar.addAction(self.actionPan)

        # basic settings end

        # add circle select

        # self.actionCircleSelect = QAction("Circle Select", self)
        # self.toolbar.addAction(self.actionCircleSelect)
        # self.actionCircleSelect.triggered.connect(self.circleSelect)

        # add Polygon Select

        self.toolPolygon = polygonSelect(self.canvas)
        self.actionPolygonSelect = QAction("Polygon Select", self)
        self.actionPolygonSelect.triggered.connect(
            lambda: self.canvas.setMapTool(self.toolPolygon)
        )
        self.toolbar.addAction(self.actionPolygonSelect)

        # add Undo
        self.actionUndo = QAction("Undo", self)
        self.toolbar.addAction(self.actionUndo)
        self.actionUndo.triggered.connect(lambda: self.removeLast)

        self.canvas.setMapTool(self.toolPan)


    def circleSelect(self):
        print("circle event triggered")
        self.canvas.circle = True

    def removeLast(self):
        pass


class Canvas(QgsMapCanvas):
    def __init__(self, lstLayer):
        super(QgsMapCanvas, self).__init__()

        self.lstLayer = lstLayer
        self.setCanvasColor(Qt.white)
        self.setLayers([self.lstLayer])
        self.setExtent(self.lstLayer.extent())
        self.circle = False
        self.polygon = False
        self.circlePoints = []
        self.polygonPoints = []