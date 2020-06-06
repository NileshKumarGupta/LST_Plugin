from qgis.core import *

from . import fileio

class groupStats(object):

    def __init__(self):

        self.features = dict()

    def polygonize(self, points):

        for fclass in points:
            polys = []
            for pointlist in points[fclass]:
                poly = [QgsPointXY(point[0], point[1]) for point in pointlist]
                polys.append(poly)
            self.features[fclass] = [QgsGeometry.fromPolygonXY([poly]) for poly in polys]
    
    def saveAll(self, folder):

        fhandler = fileio.vectorHandler(folder)
        fhandler.saveAll(self.features)
    
    def calcStats(self):

        pass

    def processAll(self, points, folder):

        self.polygonize(points)
        self.saveAll(folder)