import numpy as np
import gdal, os
from qgis.core import QgsVectorLayer, QgsFeature, QgsVectorFileWriter, QgsProject
from zipfile import ZipFile
import tarfile

from qgis.utils import iface

class fileHandler(object):

    def __init__(self):

        self.folder = ""
        self.outfolder = ""
        self.rows = 0
        self.cols = 0
        self.driver = None
        self.geoTransform = None
        self.projection = None

    def readBand(self, filepath):

        im = gdal.Open(filepath)
        array = im.ReadAsArray().astype(np.float32)
        if(not(self.folder)):
            self.folder = filepath[:filepath.rfind('/')]
        if(not(self.driver)):
            self.rows = im.RasterYSize
            self.cols = im.RasterXSize
            self.driver = im.GetDriver()
            self.geoTransform = im.GetGeoTransform()
            self.projection = im.GetProjection()
        del im
        return array

    def loadZip(self, filePaths):

        filepath = filePaths["zip"]
        recognised = False
        bands = {"Error" : None}
        for ext in [".tar.gz", ".tar", ".zip", ".gz"]:
            if(filepath.endswith(ext)):
                recognised = True
        if(not(recognised)):
            bands["Error"] = "Unknown compressed file format"
            return bands
        self.folder = filepath[:filepath.rfind("/")]

        if(filepath.endswith(".zip")):
            compressed = ZipFile(filepath, 'r')
            extract = compressed.extract
            listoffiles = compressed.namelist()
        elif(filepath.endswith(".gz")):
            compressed = tarfile.open(filepath, "r:gz")
            extract = compressed.extract
            listoffiles = [member.name for member in compressed.getmembers()]
        else:
            compressed = tarfile.open(filepath, 'r')
            extract = compressed.extract
            listoffiles = compressed.getmembers()

        for filename in listoffiles:
            if(filename.endswith("MTL.txt")):
                if(filename[:4] == "LC08"):
                    bands["sat_type"] = "Landsat8"
                    sat_type = "Landsat8"
                if(filename[:4] == "LT05"):
                    bands["sat_type"] = "Landsat5"
                    sat_type = "Landsat5"
        if("sat_type" not in bands):
            bands["Error"] = "Unknown satellite - Please verify that files have not been renamed"
            compressed.close()
            return bands

        sat_bands = {"Landsat5" : {"Red" : "B3", "Near-IR" : "B4", "Thermal-IR" : "B6"},
                "Landsat8" : {"Red" : "B4", "Near-IR" : "B5", "Thermal-IR" : "B10"} }
        filepaths = dict()
        for band in ("Red", "Near-IR", "Thermal-IR"):
            bands[band] = np.array([])
            for filename in listoffiles:
                if(filename.endswith(sat_bands[sat_type][band] + ".TIF")):
                    extract(filename)
                    filepaths[band] = filename
        compressed.close()
        for band in ("Red", "Near-IR", "Thermal-IR"):
                bands[band] = self.readBand(filepaths[band])
        return bands

    def loadBands(self, filepaths):

        """
        Gets band data as numpy arrays, from filepaths

        Inputs:
            filepaths - dictionary of bandnames (str) to paths (str)
        Outputs:
            bands - dictionary of bandnames (str) to 2d numpy arrays (int16)
        """

        bands = {"Error" : None}
        for band in filepaths:
            if(not(filepaths[band].endswith(".TIF"))):
                bands["Error"] = "Unknown band format"
                return bands
            bands[band] = self.readBand(filepaths[band])
        return bands

    def saveArray(self, array, fname):

        """
        Saves array as tiff file fname

        Inputs:
            array - numpy array
            fname - str
        Outputs:
            None
        """

        outDS = self.driver.Create(fname, self.cols, self.rows, bands=1, eType = gdal.GDT_Float32)
        outBand = outDS.GetRasterBand(1)
        outBand.WriteArray(array)
        outBand.FlushCache()
        outDS.SetGeoTransform(self.geoTransform)
        outDS.SetProjection(self.projection)

        del outDS
        del array

        """
        DavidF's answer at
        https://gis.stackexchange.com/questions/37238/writing-numpy-array-to-raster-file
        was incredibly useful.
        """

    def prepareOutFolder(self, ftype = "LSTPluginResults"):

        outfolder = self.folder + "/" + ftype
        while os.path.isdir(outfolder):
            if outfolder[-1].isnumeric():
                outfolder = outfolder[:-1] + str(1 + int(outfolder[-1]))
            else:
                outfolder += "1"
        os.makedirs(outfolder)
        self.outfolder = outfolder

    def generateFileName(self, topic, ftype):
        return self.outfolder + "/" + topic + "." + ftype

    def saveAll(self, arrays):

        if(not(self.outfolder)):
            self.prepareOutFolder()

        for resultName in arrays:
            filepath = self.generateFileName(resultName, "TIF")
            self.saveArray(arrays[resultName], filepath)

class vectorHandler(fileHandler):

    def __init__(self, folder):

        fileHandler.__init__(self)
        self.folder = folder
    
    def saveFeatures(self, polys, fname, fclass):

        uri = "MultiPolygon?crs=epsg:32643&field=id:integer&index=yes"
        vlayer = QgsVectorLayer(uri, "fclass", "memory")
        pr = vlayer.dataProvider()
        for i in range(len(polys)):
            feature = QgsFeature()
            feature.setGeometry(polys[i])
            feature.setAttributes([i])
            pr.addFeatures([feature])
        vlayer.updateExtents()
        save_options = QgsVectorFileWriter.SaveVectorOptions()
        save_options.driverName = "ESRI Shapefile"
        save_options.fileEncoding = "UTF-8"
        transform_context = QgsProject.instance().transformContext()
        writerfunc = QgsVectorFileWriter.writeAsVectorFormatV2
        error = writerfunc(vlayer, fname, transform_context, save_options)
    
    def saveAll(self, features):

        if(not(self.outfolder)):
            self.prepareOutFolder("LSTPluginShapes")
        
        for fclass in features:
            polys = features[fclass]
            fname = self.generateFileName(fclass, "shp")
            self.saveFeatures(polys, fname, fclass)
    
    def loadLayer(self, fclass):

        fname = self.generateFileName(fclass, "shp")
        layer = iface.addVectorLayer(fname, fclass, "ogr")
        return layer