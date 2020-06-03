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

        # Basic canvas settings
        self.canvas.setCanvasColor(Qt.white)
        self.canvas.setLayers([self.lstLayer])
        self.setCentralWidget(self.canvas)

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
        self.actionPan.triggered.connect(lambda: self.canvas.seteMapTool(self.toolPan))

        self.toolbar.addAction(self.actionZoomIn)
        self.toolbar.addAction(self.actionZoomOut)
        self.toolbar.addAction(self.actionPan)

        # basic settings end

        # add circle select

        self.actionCircleSelect = QAction("Circle Select", self)
        self.toolbar.addAction(self.actionCircleSelect)

        # add Polygon Select

        self.actionPolygonSelect = QAction("Polygon Select", self)
        self.toolbar.addAction(self.actionPolygonSelect)

        self.canvas.setMapTool(self.toolPan)

        def markCircle(self):
            pass

        def markPolygon(self):
            pass
