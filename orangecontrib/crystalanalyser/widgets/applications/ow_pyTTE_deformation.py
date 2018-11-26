import sys
import numpy as np
from PyQt5.QtGui import QIntValidator, QDoubleValidator
from PyQt5.QtCore import QLocale
from PyQt5.QtWidgets import QApplication, QSizePolicy
from orangewidget import gui
from orangewidget.settings import Setting
from orangewidget import widget
from oasys.widgets import widget as oasyswidget, gui as oasysgui
import orangecanvas.resources as resources
import sys,os

import pyTTE.deformation

class OWfunctions1D(oasyswidget.OWWidget):
    name = "Deformation field"
    id = "orange.widgets.pyTTEdeformation"
    description = "Calculates the deformation field for pyTTE"
    icon = "icons/functions1D.png"
    author = "Ari-Pekka Honkanen"
    author = "Ari-Pekka Honkanen"
    maintainer_email = "honkanen.ap@gmail.com"
    priority = 10
    category = ""
    keywords = ["crystalanalyser", "pyTTE","deformation"]
    outputs = [{"name": "pyTTE_deformation_data",
                "type": dict,
                "doc": "A dictionary containing deformation data"},
               # another possible output
               # {"name": "oasysaddontemplate-file",
               #  "type": str,
               #  "doc": "transfer a file"},
                ]

    # widget input (if needed)
    inputs = [{"name": "elastic_tensor_data",
               "type": dict,
               "handler": "handle_S_matrix",
               "doc": ""}]

    want_main_area = False

    THICKNESS = Setting(300.0)
    RX = Setting(1.0)
    RY = Setting(1.0)
    NU = Setting(0.27)

    S_MATRIX = Setting(None)

    def __init__(self):
        super().__init__()

        self.runaction = widget.OWAction("Set", self)
        self.runaction.triggered.connect(self.set_deformation)
        self.addAction(self.runaction)

        box0 = gui.widgetBox(self.controlArea, " ",orientation="horizontal") 
        #widget buttons: compute, set defaults, help
        gui.button(box0, self, "Set", callback=self.set_deformation)
        gui.button(box0, self, "Defaults", callback=self.defaults)
        gui.button(box0, self, "Help", callback=self.get_doc)
        self.process_showers()
        box = gui.widgetBox(self.controlArea, " ",orientation="vertical") 

        doublevalidator = QDoubleValidator()
        doublevalidator.setLocale(QLocale('C')) #This fixes the problem with decimal sepator by forcing it to '.'
        doublevalidator.setNotation(QDoubleValidator.ScientificNotation)

        self.S_MATRIX = None
                
        idx = -1 
        
        #widget index 0 
        idx += 1 
        box1 = gui.widgetBox(box) 
        gui.lineEdit(box1, self, "THICKNESS",
                     label=self.unitLabels()[idx], addSpace=True,
                    valueType=float, validator=doublevalidator)
        self.show_at(self.unitFlags()[idx], box1) 
        
        #widget index 1 
        idx += 1 
        box1 = gui.widgetBox(box) 
        gui.lineEdit(box1, self, "RX",
                     label=self.unitLabels()[idx], addSpace=True,
                    valueType=float, validator=doublevalidator)
        self.show_at(self.unitFlags()[idx], box1) 

        #widget index 2 
        idx += 1 
        box1 = gui.widgetBox(box) 
        gui.lineEdit(box1, self, "RY",
                     label=self.unitLabels()[idx], addSpace=True,
                    valueType=float, validator=doublevalidator)
        self.show_at(self.unitFlags()[idx], box1) 

        
        #widget index 2 
        idx += 1 
        box1 = gui.widgetBox(box) 
        gui.lineEdit(box1, self, "NU",
                     label=self.unitLabels()[idx], addSpace=True,
                    valueType=float, validator=doublevalidator)
        self.show_at(self.unitFlags()[idx], box1) 

        #widget index 7 
        idx += 1 
        box1 = gui.widgetBox(box) 
        gui.label(box1, self, "Using elastic constants from\nthe compliance matrix S", orientation="horizontal")
        self.show_at(self.unitFlags()[idx], box1) 
        print(idx,self.unitFlags()[idx])

        gui.rubber(self.controlArea)

    def unitLabels(self):
         return ['Crystal thickness (um)','Bending radius in\ndiffraction plane (m)','Bending radius in\nsagittal plane (m)',"Poisson's ratio",'Elastic matrix']


    def unitFlags(self):
         return ['True',          'True',       'True',            'self.S_MATRIX == None','False']

    def handle_S_matrix(self,matrix_input):
        self.S_MATRIX = matrix_input

    def set_deformation(self):

        datadict = {}
        datadict['thickness'] = self.THICKNESS
        datadict['bending_radii'] = (self.RX,self.RY)

        if self.S_MATRIX == None:
            datadict['isotropy'] = 'isotropic'
            datadict['nu'] = self.NU
            datadict['jacobian'] = pyTTE.deformation.isotropic_plate(self.RX,self.RY,self.NU,self.THICKNESS*1e-6)

        else:
            datadict['isotropy'] = 'anisotropic'
            datadict['xtal'] = self.S_MATRIX['xtal']
            datadict['hkl'] = self.S_MATRIX['hkl']
            datadict['S_matrix'] = self.S_MATRIX['S_matrix']
            datadict['jacobian'] = pyTTE.deformation.anisotropic_plate(self.RX,self.RY,self.S_MATRIX['S_matrix'],self.THICKNESS*1e-6)


        self.send("pyTTE_deformation_data",datadict)

    def defaults(self):
         self.resetSettings()
         self.set_deformation()
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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = OWfunctions1D()
    w.show()
    app.exec()
    w.saveSettings()
