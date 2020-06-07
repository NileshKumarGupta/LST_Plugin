from qgis.core import *
from qgis.analysis import *

from . import fileio

class groupStats(object):

    def __init__(self):

        self.features = dict()

    def polygonize(self, points):

        for fclass in points:
            polys = points[fclass]
            self.features[fclass] = [QgsGeometry.fromPolygonXY([poly]) for poly in polys]
    
    def saveAll(self, folder):

        self.fhandler = fileio.vectorHandler(folder)
        self.fhandler.saveAll(self.features)
    
    def calcStats(self, rlayer):

        for fclass in self.features:
            vlayer = self.fhandler.loadLayer(fclass)
            calculator = QgsZonalStatistics(vlayer, rlayer, stats = QgsZonalStatistics.Mean)
            calculator.calculateStatistics(None)

    def processAll(self, points, rlayer, folder):

        self.polygonize(points)
        self.saveAll(folder)
        self.calcStats(rlayer)