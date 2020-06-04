from qgis.PyQt.QtGui import *
from qgis.PyQt.QtWidgets import *
from qgis.PyQt.QtCore import *
from qgis.gui import QgsMapCanvas
from qgis.core import QgsRasterLayer

from . import mainLST, fileio, canvasLayer


class MainWindow(QMainWindow):
    def addCheckBox(self, text, defaultChecked=False):

        lstcheckbox = QCheckBox(text)
        lstcheckbox.setChecked(defaultChecked)
        self.layout.addWidget(lstcheckbox)
        self.checkboxes.append(lstcheckbox)

    def __init__(self, iface):

        self.iface = iface
        super(MainWindow, self).__init__()

        self.filePaths = dict()
        self.checkboxes = []
        self.layerInfor = dict()
        layers = iface.mapCanvas().layers()
        for layer in layers:
            self.layerInfor[layer.name()] = layer.dataProvider().dataSourceUri()

        # print(self.layerInfor)

        self.setWindowTitle("LST Plugin")

        self.layout = QVBoxLayout()

        # input file option
        label = QLabel()
        label.setText("Input Bands")
        label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(label)

        # input bands
        for band in ("Red", "Near-IR", "Thermal-IR"):
            self.layout.addWidget(self.browseFile(band))

        # select data type
        dtwidget = QWidget()
        hlayout = QHBoxLayout()
        label = QLabel("Select Data Type")
        lst5button = QRadioButton("Landsat5")
        lst8button = QRadioButton("Landsat8")
        lst8button.setChecked(True)
        hlayout.addWidget(label)
        hlayout.addWidget(lst5button)
        hlayout.addWidget(lst8button)
        self.radios = [lst5button, lst8button]
        dtwidget.setLayout(hlayout)
        self.layout.addWidget(dtwidget)

        label = QLabel("OR")
        label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(label)

        # select a compressed file
        zipLayout = QHBoxLayout()
        pathField = QLineEdit()
        pathField.setText("Compressed File")
        zipLayout.addWidget(pathField)
        selband = QPushButton()
        selband.setText("Select Compressed File")
        selband.clicked.connect(lambda: self.getFiles(pathField, "zip"))
        zipLayout.addWidget(selband)
        filesel = QWidget()
        filesel.setLayout(zipLayout)
        self.layout.addWidget(filesel)

        h_line = QFrame()
        h_line.setFrameShape(QFrame.HLine)
        self.layout.addWidget(h_line)

        # select output types lable
        label = QLabel()
        label.setText("Select Outputs")
        label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(label)
        # checkbox for various outputs
        self.addCheckBox("TOA Spectral Radiance")
        self.addCheckBox("At Sensor Brightness Temperature")
        self.addCheckBox("NDVI")
        self.addCheckBox("Proportion of Vegetation")
        self.addCheckBox("Land Surface Emissivity")
        self.addCheckBox("Land Surface Temperature", defaultChecked=True)
        # check through ischecked()

        h_line = QFrame()
        h_line.setFrameShape(QFrame.HLine)
        self.layout.addWidget(h_line)

        # go button
        goButton = QPushButton("Go")
        goButton.clicked.connect(self.goFunc)
        self.layout.addWidget(goButton)

        h_line = QFrame()
        h_line.setFrameShape(QFrame.HLine)
        self.layout.addWidget(h_line)

        mainWidget = QWidget()
        mainWidget.setLayout(self.layout)
        self.setCentralWidget(mainWidget)

        self.status = QStatusBar()
        self.setStatusBar(self.status)

    def browseFile(self, band):
        filesel = QWidget()
        hlayout = QHBoxLayout()

        pathField = QLineEdit()
        pathField.setText(band)
        hlayout.addWidget(pathField)

        selLayer = QComboBox()
        selLayer.addItem("Select a Layer")
        self.layerInfor["Select a Layer"] = "Select a layer"

        for name in self.layerInfor:
            selLayer.addItem(name)
        selLayer.activated.connect(
            lambda: self.getLayers(
                pathField, self.layerInfor[selLayer.currentText()], band
            )
        )
        hlayout.addWidget(selLayer)
        hlayout.addWidget(QLabel("Or"))

        selband = QPushButton()
        selband.setText("Select a File")
        selband.clicked.connect(lambda: self.getFiles(pathField, band))
        hlayout.addWidget(selband)
        filesel.setLayout(hlayout)
        return filesel

    def getLayers(self, pathField, addr, band):
        if addr == "Select a layer":
            return
        pathField.setText(addr)
        self.filePaths[band] = addr

    def getFiles(self, pathField, band):
        fp = QFileDialog.getOpenFileName()
        if not (fp[0]):
            return
        pathField.setText(fp[0])
        self.filePaths[band] = fp[0]

    def goFunc(self):

        resultStates = []
        for box in self.checkboxes:
            resultStates.append(box.isChecked())

        satType = (
            self.radios[0].text()
            if self.radios[0].isChecked()
            else self.radios[1].text()
        )

        layers = mainLST.processAll(self, self.filePaths, resultStates, satType)

        if("LST" in layers):
            lstLayer = layers["LST"]
            zoneSelect = canvasLayer.CanvasLayer(lstLayer)
            zoneSelect.show()

        # lstLayer = self.iface.mapCanvas().layers()[0]


    def showStatus(self, text):
        self.status.showMessage(text, 20000)

    def showError(self, err):
        self.showStatus(err)
        messageBox = QMessageBox()
        messageBox.critical(None, "", err)
