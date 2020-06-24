from qgis.core import *
from qgis.analysis import *

from . import fileio
import time

class groupStats(object):

    def __init__(self):

        self.features = dict()
        self.form = None

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
    
    def calcStats(self, rlayer, fclass):

        vlayer = self.layers[fclass]
        statsreq = QgsZonalStatistics.Statistics(QgsZonalStatistics.Mean | QgsZonalStatistics.StDev)
        calculator = QgsZonalStatistics(vlayer, rlayer, stats = statsreq)
        calculator.calculateStatistics(None)
        mpoly = list(vlayer.getFeatures())[0]
        mean, stdev = list(mpoly.attributes())[1:]
        return mean, stdev
    
    def update(self, text):

        text = str(text)
        if(not(self.form)):
            return
        self.form.showStatus(text)

    def processAll(self, form, points, rlayer, folder):

        self.form = form
        self.update("Preparing multipolygons")
        self.multipolygonize(points)
        self.update("Saving shape files")
        self.saveAll(folder)
        self.update("Loading vector layers")
        self.getLayers(points)

        stats = dict()
        for fclass in self.features:
            self.update("Calculating Statistics for " + fclass)
            stats[fclass] = self.calcStats(rlayer, fclass)

        self.update("Finished")
        return stats