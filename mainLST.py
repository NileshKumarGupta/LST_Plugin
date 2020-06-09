from qgis.PyQt.QtGui import *
from qgis.PyQt.QtWidgets import *
from qgis.PyQt.QtCore import *
from qgis.utils import iface
from qgis.gui import QgsMapCanvas

import os

# neccesary
from . import resources, form, procedures, fileio, canvasLayer

## Main class: LSTplugin


class LSTplugin(object):

    """Main plugin object"""

    def __init__(self, iface):

        """
        Initialiser
        """

        self.iface = iface

    def initGui(self):

        """
        Called when loaded
        Adds plugin option to menus
        """

        self.action = QAction(
            icon=QIcon(":plugins/LST_Plugin/icon.png"),
            text="LST plugin",
            parent=self.iface.mainWindow(),
        )
        self.action.triggered.connect(self.run)

        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu("LST Plugin", self.action)

    def unload(self):

        """
        Called when plugin is unloaded
        Removes option from interface
        """

        self.iface.removePluginMenu("LST Plugin", self.action)
        self.iface.removeToolBarIcon(self.action)

    def run(self):

        """
        Called when plugin asked to run
        Starts a UI instance, defined in form.py
        """

        window = form.MainWindow(self.iface)
        window.show()

def displayOnScreen(resultStates, resultNames, filer):

    """
    Display generated outputs as layers on the interface
    """

    layers = dict()
    for i in range(6):
        if resultStates[i]:
            layers[resultNames[i]] = iface.addRasterLayer(
                filer.generateFileName(resultNames[i], "TIF"), resultNames[i]
            )
    return layers

def processAll(form, filePaths, resultStates, satType, displayResults=True):

    """
    Main processing element, called every time Go is pressed
    """

    form.showStatus("Loading Files")

    filer = fileio.fileHandler()
    processor = procedures.processor()

    if "zip" in filePaths:
        bands = filer.loadZip(filePaths)
        satType = bands["sat_type"]
        del bands["sat_type"]
    else:
        bands = filer.loadBands(filePaths)
    if bands["Error"]:
        form.showError(bands["Error"])
        return
    del bands["Error"]

    form.showStatus("Processing")

    results = processor.process(bands, satType, resultStates, form)
    if results["Error"]:
        form.showError(results["Error"])
        return
    del results["Error"]

    form.showStatus("Saving Outputs")

    filer.saveAll(results)

    form.showStatus("Displaying Outputs")

    layers = None
    resultNames = ["TOA", "BT", "NDVI", "PV", "LSE", "LST"]
    if displayResults:
        layers = displayOnScreen(resultStates, resultNames, filer)

    form.showStatus("Finished")

    return layers, filer.folder