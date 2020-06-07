from qgis.core import *
from qgis.analysis import *

from . import fileio

class groupStats(object):

    def __init__(self):

        self.features = dict()

    def multipolygonize(self, points):

        for fclass in points:
            polys = points[fclass]
            polys = [[poly] for poly in polys]
            self.features[fclass] = QgsGeometry.fromMultiPolygonXY(polys)
    
    def saveAll(self, folder):

        self.fhandler = fileio.vectorHandler(folder)
        self.fhandler.saveAll(self.features)
    
    def getLayers(self, points):

        self.layers = dict()
        for fclass in points:
            self.layers[fclass] = self.fhandler.loadLayer(fclass)
    
    def calcStats(self, rlayer):

        self.stats = dict()
        for fclass in self.features:
            vlayer = self.layers[fclass]
            statsreq = QgsZonalStatistics.Statistics(QgsZonalStatistics.Mean | QgsZonalStatistics.StDev)
            calculator = QgsZonalStatistics(vlayer, rlayer, stats = statsreq)
            calculator.calculateStatistics(None)
            self.stats[fclass] = None

    def processAll(self, form, points, rlayer, folder):

        self.multipolygonize(points)
        self.saveAll(folder)
        self.getLayers(points)
        self.calcStats(rlayer)
        form.showStatus("Calced stats")