from qgis.PyQt.QtGui import *
from qgis.PyQt.QtWidgets import *
from qgis.PyQt.QtCore import *
from qgis.gui import QgsMapCanvas
from qgis.core import QgsRasterLayer


# class CanvasLayer(QWidget):
#     def __init__(self, lstLayer):
#         super(CanvasLayer, self).__init__()
#         self.lstLayer = lstLayer
#         self.layout = QVBoxLayout()

#         # two components, one for toolbar, the other one for showing the layer

#         # toolbar
#         # tool for marking a circle
#         # tool for marking a polygon
#         self.toolbar = QWidget()
#         hlayout = QHBoxLayout()
#         hlayout.setAlignment(Qt.AlignLeft)

#         circleButton = QPushButton("Select a Circle")
#         circleButton.clicked.connect(self.markCircle)
#         hlayout.addWidget(circleButton)

#         polygonButton = QPushButton("Select a Polygon")
#         polygonButton.clicked.connect(self.markPolygon)
#         hlayout.addWidget(polygonButton)

#         self.toolbar.setLayout(hlayout)
#         # canvas element
#         self.canvas = QgsMapCanvas()
#         self.canvas.setCanvasColor(Qt.white)
#         self.canvas.setExtent(layer.extent())
#         self.canvas.setLayers([layer])
#         # to do add basic properties of canvas

#         self.layout.addWidget(self.toolbar)
#         # self.layout.addWidget(self.canvas)

#     def markCircle(self):
#         pass

#     def markPolygon(self):
#         pass

class CanvasLayer(QMainWindow):
    def __init__(self, lstLayer):
        super(self, QMainWindow).__init__()

        self.lstLayer = lstLayer

        self.canvas = QgsMapCanvas()
        self.canvas.setCanvasColor(Qt.white)
        self.canvas.setLayers([self.lstLayer])
        self.centralWidget(self.canvas)

        self.actionZoomIn = QAction("Zoom in", self)
        self.actionZoomOut = QAction("Zoom out", self)
        self.actionPan = QAction("Pan", self)



  self.canvas = QgsMapCanvas()

        self.canvas.setLayers([layer])

        self.setCentralWidget(self.canvas)

        self.actionZoomIn = QAction("Zoom in", self)
        self.actionZoomOut = QAction("Zoom out", self)
        self.actionPan = QAction("Pan", self)

        self.actionZoomIn.setCheckable(True)
        self.actionZoomOut.setCheckable(True)
        self.actionPan.setCheckable(True)

        self.actionZoomIn.triggered.connect(self.zoomIn)
        self.actionZoomOut.triggered.connect(self.zoomOut)
        self.actionPan.triggered.connect(self.pan)

        self.toolbar = self.addToolBar("Canvas actions")
        self.toolbar.addAction(self.actionZoomIn)
        self.toolbar.addAction(self.actionZoomOut)
        self.toolbar.addAction(self.actionPan)

        # create the map tools
        self.toolPan = QgsMapToolPan(self.canvas)
        self.toolPan.setAction(self.actionPan)
        self.toolZoomIn = QgsMapToolZoom(self.canvas, False) # false = in
        self.toolZoomIn.setAction(self.actionZoomIn)
        self.toolZoomOut = QgsMapToolZoom(self.canvas, True) # true = out
        self.toolZoomOut.setAction(self.actionZoomOut)

        self.pan()

    def zoomIn(self):
        self.canvas.setMapTool(self.toolZoomIn)

    def zoomOut(self):
        self.canvas.setMapTool(self.toolZoomOut)

    def pan(self):
        self.canvas.setMapTool(self.toolPan)
