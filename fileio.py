import numpy as np
import gdal, os, tarfile
from zipfile import ZipFile
import processing
from qgis.core import *

gdal.UseExceptions()

from qgis.utils import iface


class fileHandler(object):

    """
    Class to handle all file input output operations
    """

    def __init__(self):

        self.folder = ""  ## Folder in which all operations are ongoing
        self.outfolder = ""  ## Folder in which to place outputs

        ## Tif writing data, copied from input
        self.rows = 0
        self.cols = 0
        self.driver = None
        self.geoTransform = None
        self.projection = None

    def readBand(self, filepath):

        """
        Given a filepath, read a numpy array from its data
        Save tif data for future use, if the class has not already done so
        """

        print("reading " + filepath)

        im = gdal.Open(filepath)
        array = im.ReadAsArray().astype(np.float32)
        if not (self.folder):
            self.folder = filepath[: filepath.rfind("/")]
            print("Operating folder - " + self.folder)
        if not (self.driver):
            self.rows = im.RasterYSize
            self.cols = im.RasterXSize
            self.driver = im.GetDriver()
            self.geoTransform = im.GetGeoTransform()
            self.projection = im.GetProjection()
            layer = QgsRasterLayer(filepath, "Temp")
            self.extent = layer.extent()
            self.crs = layer.crs()
        del im
        print("Read array of shape", array.shape[0], array.shape[1])
        return array

    def loadZip(self, filePaths):

        """
        Compatible with zip, tar and gz extensions
        Read only Red, Near IR and Thermal IR bands
        Get satellite type by looking at the name of the metadata file.
        """

        filepath = filePaths["zip"]
        recognised = False
        bands = {"Error": None}
        for ext in [".tar.gz", ".tar", ".zip", ".gz"]:
            if(filepath.lower().endswith(ext)):
                recognised = True
        if not (recognised):
            bands["Error"] = "Unknown compressed file format"
            return bands
        self.folder = filepath[: filepath.rfind("/")]

        if(filepath.lower().endswith(".zip")):
            compressed = ZipFile(filepath, 'r')
            extract = compressed.extract
            listoffiles = compressed.namelist()
        elif(filepath.lower().endswith(".gz")):
            compressed = tarfile.open(filepath, "r:gz")
            extract = compressed.extract
            listoffiles = [member.name for member in compressed.getmembers()]
        else:
            compressed = tarfile.open(filepath, "r")
            extract = compressed.extract
            listoffiles = compressed.getmembers()

        for filename in listoffiles:
            if(filename.upper().endswith("MTL.TXT")):
                if(filename[:4] == "LC08"):
                    bands["sat_type"] = "Landsat8"
                    sat_type = "Landsat8"
                if filename[:4] == "LT05":
                    bands["sat_type"] = "Landsat5"
                    sat_type = "Landsat5"
        if "sat_type" not in bands:
            bands[
                "Error"
            ] = "Unknown satellite - Please verify that files have not been renamed"
            compressed.close()
            return bands

        sat_bands = {"Landsat5" : {"Red" : "B3", "Near-IR" : "B4", "Thermal-IR" : "B6"},
                "Landsat8" : {"Red" : "B4", "Near-IR" : "B5", "Thermal-IR" : "B10"} }

        shapefile = None
        if("Shape" in filePaths):
            shapefile = filePaths["Shape"]

        filePaths = dict()
        for band in ("Red", "Near-IR", "Thermal-IR"):
            bands[band] = np.array([])
            for filename in listoffiles:
                if(filename.upper().endswith(sat_bands[sat_type][band] + ".TIF")):
                    extract(filename)
                    filePaths[band] = filename
        compressed.close()
        print("Zipped filepaths - ")
        print(filePaths)
        for band in ("Red", "Near-IR", "Thermal-IR"):
            bands[band] = self.readBand(filePaths[band])

        if(shapefile):
            print("Opening shapefile")
            bands["Shape"] = self.readShapeFile(shapefile)
            print("Shapefile ready (or error to be raised)")
            if(type(bands["Shape"]) == str):
                bands["Error"] = bands["Shape"]
                return bands
        return bands

    def loadBands(self, filepaths):

        """
        Gets band data as numpy arrays, from a dict of filepaths
        """

        bands = {"Error": None}
        print("Reading bands - ")
        print(bands)
        for band in filepaths:
            if(band == "Shape"):
                print("Shape encountered")
                continue
            if(not(filepaths[band].lower().endswith(".tif"))):
                bands["Error"] = "Bands must be TIFs"
                return bands
            bands[band] = self.readBand(filepaths[band])
        if("Shape" in filepaths):
            bands["Shape"] = self.readShapeFile(filepaths["Shape"])
            if(type(bands["Shape"]) == str):
                bands["Error"] = bands["Shape"]
                return bands
        return bands
    
    def readShapeFile(self, vectorfname):

        """
        Get a rasterized numpy array from the features of a shapefile
        """
        
        print("Reading " + vectorfname + " as shapefile")
        if(not(vectorfname.lower().endswith(".shp"))):
            return "Shapes must be SHPs"
        print("Loading shapefile")
        vlayer = self.loadVectorLayer(vectorfname)
        shapefile = self.generateFileName("Shape", "TIF")
        print("Calling rasterize")
        self.rasterize(vlayer, shapefile)
        print("Shape ready")
        return self.readBand(shapefile)

    def saveArray(self, array, fname):

        """
        Saves array as tiff file named fname
        Use TIF info saved by the class on input
        Should not be used directly, use saveAll instead
        """

        print("Saving array in " + fname)

        outDS = self.driver.Create(
            fname, self.cols, self.rows, bands=1, eType=gdal.GDT_Float32
        )
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
    
    def loadVectorLayer(self, fname):

        """
        Load a vector layer, using qgis core functionality
        """

        layer = QgsVectorLayer(fname, "Shape", "ogr")
        return layer
    
    def rasterize(self, vlayer, fname, res = 30):

        """
        Convert a vector layer to a raster layer, handle CRS differences
        """

        rfile = self.driver.Create(fname, self.cols, self.rows, bands=1, eType = gdal.GDT_Float32)
        rfile.SetProjection(self.projection)
        rfile.SetGeoTransform(self.geoTransform)
        rfile = None

        print("CRS types - dest: ", self.crs, "source", vlayer.crs())

        if(self.crs != vlayer.crs()):
            parameters = {"INPUT" : vlayer, "TARGET_CRS" : self.crs, "OUTPUT" : "TEMPORARY_OUTPUT"}
            vlayer = processing.run("native:reprojectlayer", parameters)["OUTPUT"]
            print("CRS converted")

        xmin = self.extent.xMinimum()
        xmax = self.extent.xMaximum()
        ymin = self.extent.yMinimum()
        ymax = self.extent.yMaximum()

        parameters = {
            "INPUT" : vlayer,
            "HEIGHT": res,
            "WIDTH" : res,
            "BURN"  : 0,
            "UNITS" : 1,
            "EXTENT":"%f,%f,%f,%f"% (xmin, xmax, ymin, ymax),
            "DATA_TYPE" : 5,
            "NODATA" : 1,
            "OUTPUT": fname
        }
        print("Using parameters for rasterize -")
        print(parameters)
        processing.run("gdal:rasterize", parameters)
        vlayer = None

    def prepareOutFolder(self, ftype="LSTPluginResults"):

        """
        Make a new directory under the operating folder, for outputs
        """

        outfolder = self.folder + "/LSTOutputs"
        while os.path.isdir(outfolder):
            if outfolder[-1].isnumeric():
                outfolder = outfolder[:-1] + str(1 + int(outfolder[-1]))
            else:
                outfolder += "1"
        os.makedirs(outfolder)
        self.outfolder = outfolder
        print("Outfolder - " + self.outfolder)

    def generateFileName(self, topic, ftype):

        """
        Generate a filepath for topic
        """
        
        if(not(self.outfolder)):
            self.prepareOutFolder()
        return self.outfolder + "/" + topic + "." + ftype

    def saveAll(self, arrays):

        """
        Write each of a dict of arrays as TIF outputs
        """

        if not (self.outfolder):
            self.prepareOutFolder()

        for resultName in arrays:
            filepath = self.generateFileName(resultName, "TIF")
            self.saveArray(arrays[resultName], filepath)


class vectorHandler(fileHandler):
    def __init__(self, folder):

        fileHandler.__init__(self)
        self.folder = folder

    def saveFeatures(self, mpoly, fname, fclass):

        uri = "MultiPolygon?crs=epsg:32643&field=id:integer&index=yes"
        vlayer = QgsVectorLayer(uri, "fclass", "memory")
        pr = vlayer.dataProvider()
        feature = QgsFeature()
        feature.setGeometry(mpoly)
        feature.setAttributes([0])
        pr.addFeatures([feature])
        vlayer.updateExtents()
        save_options = QgsVectorFileWriter.SaveVectorOptions()
        save_options.driverName = "ESRI Shapefile"
        save_options.fileEncoding = "UTF-8"
        transform_context = QgsProject.instance().transformContext()
        writerfunc = QgsVectorFileWriter.writeAsVectorFormatV2
        error = writerfunc(vlayer, fname, transform_context, save_options)

    def saveAll(self, features):

        if not (self.outfolder):
            self.prepareOutFolder("LSTPluginShapes")

        for fclass in features:
            mpoly = features[fclass]
            fname = self.generateFileName(fclass, "shp")
            self.saveFeatures(mpoly, fname, fclass)

    def loadLayer(self, fclass):

        fname = self.generateFileName(fclass, "shp")
        layer = iface.addVectorLayer(fname, fclass, "ogr")
        return layer
