import sys
import numpy as np
from PyQt5.QtGui import QIntValidator, QDoubleValidator
from PyQt5.QtWidgets import QApplication, QSizePolicy
from orangewidget import gui
from orangewidget.settings import Setting
from orangewidget import widget
from oasys.widgets import widget as oasyswidget, gui as oasysgui
import orangecanvas.resources as resources
import sys,os

class OWfunctions1D(oasyswidget.OWWidget):
    name = "functions1D"
    id = "orange.widgets.datafunctions1D"
    description = "Application to compute..."
    icon = "icons/functions1D.png"
    author = "create_widget.py"
    maintainer_email = "srio@esrf.eu"
    priority = 10
    category = ""
    keywords = ["oasysaddontemplate", "functions1D"]
    outputs = [{"name": "oasysaddontemplate-data",
                "type": np.ndarray,
                "doc": "transfer numpy arrays"},
               # another possible output
               # {"name": "oasysaddontemplate-file",
               #  "type": str,
               #  "doc": "transfer a file"},
                ]

    # widget input (if needed)
    #inputs = [{"name": "Name",
    #           "type": type,
    #           "handler": None,
    #           "doc": ""}]

    want_main_area = False

    FROM = Setting(-100.0)
    TO = Setting(100.0)
    NPOINTS = Setting(500)
    FUNCTION_NAME = Setting(3)
    CUSTOM = Setting("np.sin(x)")
    DUMP_TO_FILE = Setting(0)
    FILE_NAME = Setting("tmp.dat")


    def __init__(self):
        super().__init__(self)

        self.runaction = widget.OWAction("Compute", self)
        self.runaction.triggered.connect(self.compute)
        self.addAction(self.runaction)

        box0 = gui.widgetBox(self.controlArea, " ",orientation="horizontal") 
        #widget buttons: compute, set defaults, help
        gui.button(box0, self, "Compute", callback=self.compute)
        gui.button(box0, self, "Defaults", callback=self.defaults)
        gui.button(box0, self, "Help", callback=self.get_doc)
        self.process_showers()
        box = gui.widgetBox(self.controlArea, " ",orientation="vertical") 
        
        
        idx = -1 
        
        #widget index 0 
        idx += 1 
        box1 = gui.widgetBox(box) 
        gui.lineEdit(box1, self, "FROM",
                     label=self.unitLabels()[idx], addSpace=True,
                    valueType=float, validator=QDoubleValidator())
        self.show_at(self.unitFlags()[idx], box1) 
        
        #widget index 1 
        idx += 1 
        box1 = gui.widgetBox(box) 
        gui.lineEdit(box1, self, "TO",
                     label=self.unitLabels()[idx], addSpace=True,
                    valueType=float, validator=QDoubleValidator())
        self.show_at(self.unitFlags()[idx], box1) 
        
        #widget index 2 
        idx += 1 
        box1 = gui.widgetBox(box) 
        gui.lineEdit(box1, self, "NPOINTS",
                     label=self.unitLabels()[idx], addSpace=True,
                    valueType=int, validator=QIntValidator())
        self.show_at(self.unitFlags()[idx], box1) 
        
        #widget index 3 
        idx += 1 
        box1 = gui.widgetBox(box) 
        gui.comboBox(box1, self, "FUNCTION_NAME",
                     label=self.unitLabels()[idx], addSpace=True,
                    items=['sin(x)', 'cos(x)', 'x^2+x+1', 'Custom'],
                    valueType=int, orientation="horizontal")
        self.show_at(self.unitFlags()[idx], box1) 
        
        #widget index 4 
        idx += 1 
        box1 = gui.widgetBox(box) 
        gui.lineEdit(box1, self, "CUSTOM",
                     label=self.unitLabels()[idx], addSpace=True)
        self.show_at(self.unitFlags()[idx], box1) 
        
        #widget index 5 
        idx += 1 
        box1 = gui.widgetBox(box) 
        gui.comboBox(box1, self, "DUMP_TO_FILE",
                     label=self.unitLabels()[idx], addSpace=True,
                    items=['Yes', 'No'],
                    valueType=int, orientation="horizontal")
        self.show_at(self.unitFlags()[idx], box1) 
        
        #widget index 6 
        idx += 1 
        box1 = gui.widgetBox(box) 
        gui.lineEdit(box1, self, "FILE_NAME",
                     label=self.unitLabels()[idx], addSpace=True)
        self.show_at(self.unitFlags()[idx], box1) 

        gui.rubber(self.controlArea)

    def unitLabels(self):
         return ['Abscissa from ','Abscissa to','Number of points','Function','Custom expression',      'Dump to file','File name']


    def unitFlags(self):
         return ['True',          'True',       'True',            'True',    'self.FUNCTION_NAME == 3','True',        'self.DUMP_TO_FILE == 0']


    def compute(self):
        dataArray = OWfunctions1D.calculate_external_functions1D(FROM=self.FROM,TO=self.TO,NPOINTS=self.NPOINTS,FUNCTION_NAME=self.FUNCTION_NAME,CUSTOM=self.CUSTOM,DUMP_TO_FILE=self.DUMP_TO_FILE,FILE_NAME=self.FILE_NAME)

        # if fileName == None:
        #     print("No file to send")
        # else:
        #     self.send("oasysaddontemplate-file",fileName)

        self.send("oasysaddontemplate-data",dataArray)


    def defaults(self):
         self.resetSettings()
         self.compute()
         return

    def get_doc(self):
        print("help pressed.")
        home_doc = resources.package_dirname("orangecontrib.oasysaddontemplate") + "/doc_files/"
        filename1 = os.path.join(home_doc,'functions1D'+'.txt')
        print("Opening file %s"%filename1)
        if sys.platform == 'darwin':
            command = "open -a TextEdit "+filename1+" &"
        elif sys.platform == 'linux':
            command = "gedit "+filename1+" &"
        os.system(command)


    #
    # this is the calculation method to be implemented by the user
    # It is defined as static method to get all inputs from the arguments so it
    # can easily moved outside the class
    #
    @staticmethod
    def calculate_external_functions1D(FROM=-100.0,TO=100.0,NPOINTS=500,FUNCTION_NAME=3,CUSTOM="np.sin(x)",DUMP_TO_FILE=0,FILE_NAME="tmp.dat"):
        print("Inside calculate_external_functions1D. ")

        # A MERE EXAMPLE
        a = np.array([
        [  8.47091837e+04,  8.57285714e+04,   8.67479592e+04, 8.77673469e+04,] ,
        [  1.16210756e+12,  1.10833975e+12,   1.05700892e+12, 1.00800805e+12]
        ])

        return a


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = OWfunctions1D()
    w.show()
    app.exec()
    w.saveSettings()
