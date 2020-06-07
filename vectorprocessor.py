from qgis.core import *

from . import fileio

class groupStats(object):

    def __init__(self):

        self.features = dict()

    def polygonize(self, points):

        for fclass in points:
            polys = points[fclass]
            self.features[fclass] = [QgsGeometry.fromPolygonXY([poly]) for poly in polys]
    
    def saveAll(self, folder):

        fhandler = fileio.vectorHandler(folder)
        fhandler.saveAll(self.features)
    
    def calcStats(self):

        pass

    def processAll(self, points, folder):

        self.polygonize(points)
        self.saveAll(folder)