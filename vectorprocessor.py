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
            mpoly = list(vlayer.getFeatures())[0]
            mean, stdev = list(mpoly.attributes())[1:]
            self.stats[fclass] = (mean, stdev)

    def processAll(self, form, points, rlayer, folder):

        form.showStatus("Preparing multipolygons")
        self.multipolygonize(points)
        form.showStatus("Saving shape files")
        self.saveAll(folder)
        form.showStatus("Loading vector layers")
        self.getLayers(points)
        form.showStatus("Calculating Statistics")
        self.calcStats(rlayer)
        form.showStatus("Finished")
        return self.stats