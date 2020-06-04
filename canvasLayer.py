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


class circleSelect(QgsMapTool):
    def __init__(self, canvas):

        QgsMapTool.__init__(self, canvas)
        self.canvas = canvas

    def canvasPressEvent(self, event):

        pass


class CanvasLayer(QMainWindow):
    def __init__(self, lstLayer):
        super(QMainWindow, self).__init__()
        self.lstLayer = lstLayer
        self.canvas = QgsMapCanvas()
        self.toolbar = self.addToolBar("Canvas actions")
        self.setCentralWidget(self.canvas)

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
        self.actionPan.triggered.connect(lambda: self.canvas.setMapTool(self.pan))

        self.toolbar.addAction(self.actionZoomIn)
        self.toolbar.addAction(self.actionZoomOut)
        self.toolbar.addAction(self.actionPan)

        # basic settings end

        # add circle select

        self.toolCircle = circleSelect(self.canvas)
        self.actionCircleSelect = QAction("Circle Select", self)
        self.actionCircleSelect.triggered.connect(
            lambda: self.canvas.setMapTool(self.toolCircle)
        )
        self.toolbar.addAction(self.actionCircleSelect)
        # self.actionCircleSelect.triggered.connect(self.circleSelect)

        # add Polygon Select

        self.toolPolygon = polygonSelect(self.canvas)
        self.actionPolygonSelect = QAction("Polygon Select", self)
        self.actionPolygonSelect.triggered.connect(
            lambda: self.canvas.setMapTool(self.toolPolygon)
        )
        self.toolbar.addAction(self.actionPolygonSelect)
        self.toolPolygon = PolygonMapTool(self.canvas)
        self.toolPolygon.setAction(self.actionPolygonSelect)
        self.actionPolygonSelect.triggered.connect(
            lambda: self.canvas.setMapTool(self.toolPolygon)
        )
        # self.actionPolygonSelect.triggered.connect(self.polygonSelect)

        # add Undo
        self.actionUndo = QAction("Undo", self)
        self.toolbar.addAction(self.actionUndo)
        self.actionUndo.triggered.connect(lambda: self.removeLast)

        # self.canvas.setMapTool(self.toolPan)

    def removeLast(self):
        pass


class PolygonMapTool(QgsMapToolEmitPoint):
    def __init__(self, canvas):
        self.canvas = canvas

        QgsMapToolEmitPoint.__init__(self, self.canvas)

        self.rubberBand = QgsRubberBand(self.canvas, True)
        self.rubberBand.setColor(Qt.red)
        self.rubberBand.setWidth(1)
        self.rubberBand.reset()
        self.pointList = list()
        self.polygonList = list()

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
            self.rubberBand.show()
