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

def rotation_matrix(hkl):
    '''
        Computes the rotation matrix which aligns the given hkl along z-axis.
        NOTE: works currently only for the cubic systems
    '''

    if hkl[0] or hkl[1]:
        #rotation axis
        u = -np.array([[hkl[1]],[-hkl[0]]])/np.sqrt(hkl[0]**2+hkl[1]**2)
        #rotation angle
        th = np.arccos(hkl[2]/np.sqrt(hkl[0]**2+hkl[1]**2+hkl[2]**2))

        #rotation matrix
        R=np.array([[np.cos(th)+u[0]**2*(1-np.cos(th)), u[0]*u[1]*(1-np.cos(th)), u[1]*np.sin(th)],
           [u[0]*u[1]*(1-np.cos(th)), np.cos(th)+u[1]**2*(1-np.cos(th)), -u[0]*np.sin(th)],
           [-u[1]*np.sin(th), u[0]*np.sin(th), np.cos(th)]])
    else:
        R=np.array([[1,0,0],[0,1,0],[0,0,1]])

    return R.transpose()


def compute_elastic_matrices(zdir, xtal):
    '''
        Computes the compliance and stiffness matrices S and C a given z-direction.
        The x- and y-directions are determined automatically 
    '''
    xtal = xtal.lower()

    #TODO: read the elastic constants from a file 
    if xtal == 'ge':
    	c1111, c1122, c2323 = 1.292, 0.479, 0.670
    elif xtal == 'si':
    	c1111, c1122, c2323 = 1.657, 0.639, 0.796
    else:
        raise ValueError('Elastic parameters for the crystal not found!')

    #TODO: generalize to other systems alongside the cubic as well
    Cc = np.zeros((3,3,3,3))

    Cc[0,0,0,0], Cc[1,1,1,1], Cc[2,2,2,2] = c1111, c1111, c1111
    Cc[0,0,1,1], Cc[0,0,2,2], Cc[1,1,0,0] = c1122, c1122, c1122
    Cc[1,1,2,2], Cc[2,2,0,0], Cc[2,2,1,1] = c1122, c1122, c1122

    Cc[0,2,0,2], Cc[2,0,0,2], Cc[0,2,2,0], Cc[2,0,2,0] = c2323, c2323, c2323, c2323
    Cc[1,2,1,2], Cc[2,1,1,2], Cc[1,2,2,1], Cc[2,1,2,1] = c2323, c2323, c2323, c2323
    Cc[0,1,0,1], Cc[1,0,0,1], Cc[0,1,1,0], Cc[1,0,1,0] = c2323, c2323, c2323, c2323

    Q = rotation_matrix(zdir)
   
    #Rotate the tensor
    #New faster version according to
    #http://stackoverflow.com/questions/4962606/fast-tensor-rotation-with-numpy

    QQ = np.outer(Q,Q)
    QQQQ = np.outer(QQ,QQ).reshape(4*Q.shape)
    axes = ((0, 2, 4, 6), (0, 1, 2, 3))
    Crot = np.tensordot(QQQQ, Cc, axes)
    
    #Assemble the stiffness matrix
    C = np.array([
        [Crot[0,0,0,0], Crot[0,0,1,1], Crot[0,0,2,2], Crot[0,0,1,2], Crot[0,0,0,2], Crot[0,0,0,1]],
        [Crot[1,1,0,0], Crot[1,1,1,1], Crot[1,1,2,2], Crot[1,1,1,2], Crot[1,1,0,2], Crot[1,1,0,1]],
        [Crot[2,2,0,0], Crot[2,2,1,1], Crot[2,2,2,2], Crot[2,2,1,2], Crot[2,2,0,2], Crot[2,2,0,1]],
        [Crot[2,1,0,0], Crot[2,1,1,1], Crot[2,1,2,2], Crot[1,2,1,2], Crot[1,2,0,2], Crot[1,2,0,1]],
        [Crot[2,0,0,0], Crot[2,0,1,1], Crot[2,0,2,2], Crot[2,0,1,2], Crot[0,2,0,2], Crot[2,0,0,1]],
        [Crot[1,0,0,0], Crot[1,0,1,1], Crot[1,0,2,2], Crot[1,0,1,2], Crot[1,0,0,2], Crot[0,1,0,1]]
    ]).reshape((6,6))
    
    
    C=C*1e11 #in pascal
    S = np.linalg.inv(C)

    return S, C


class OWfunctions1D(oasyswidget.OWWidget):
    name = "Crystal elastic matrices"
    id = "orange.widgets.pyTTEelastictensors"
    description = "Calculates the rotated elastic tensors for anisotropic crystals"
    icon = "icons/functions1D.png"
    author = "Ari-Pekka Honkanen"
    author = "Ari-Pekka Honkanen"
    maintainer_email = "honkanen.ap@gmail.com"
    priority = 10
    category = ""
    keywords = ["crystalanalyser", "pyTTE","elasticity"]
    outputs = [{"name": "elastic_tensor_data",
               "type": dict,
               "doc": ""}]
               # another possible output
               # {"name": "oasysaddontemplate-file",
               #  "type": str,
               #  "doc": "transfer a file"},

    # widget input (if needed)
    #inputs = [{"name": "compliance_matrix",
    #           "type": dict,
    #           "handler": "handle_S_matrix",
    #           "doc": ""}]

    want_main_area = False

    CRYSTAL_MATERIAL = Setting(0)
    MILLER_INDEX_H = Setting(1)
    MILLER_INDEX_K = Setting(1)
    MILLER_INDEX_L = Setting(1)

    S_MATRIX_STR = Setting('')
    C_MATRIX_STR = Setting('')

    def __init__(self):
        super().__init__()

        self.runaction = widget.OWAction("Calculate", self)
        self.runaction.triggered.connect(self.calculate)
        self.addAction(self.runaction)

        box0 = gui.widgetBox(self.controlArea, " ",orientation="horizontal") 
        #widget buttons: compute, set defaults, help
        gui.button(box0, self, "Calculate", callback=self.calculate)
        gui.button(box0, self, "Defaults", callback=self.defaults)
        gui.button(box0, self, "Help", callback=self.get_doc)
        self.process_showers()
        parentbox = gui.widgetBox(self.controlArea, " ",orientation="horizontal") 

        boxa = gui.widgetBox(parentbox, " ",orientation="vertical") 
        boxb = gui.widgetBox(parentbox, " ",orientation="vertical") 

        doublevalidator = QDoubleValidator()
        doublevalidator.setLocale(QLocale('C')) #This fixes the problem with decimal sepator by forcing it to '.'
        doublevalidator.setNotation(QDoubleValidator.ScientificNotation)

        self.S_MATRIX_STR = ''
        self.C_MATRIX_STR = ''
                
        idx = -1 


        #widget index 0 
        idx += 1 
        box1 = gui.widgetBox(boxa) 
        gui.comboBox(box1, self, "CRYSTAL_MATERIAL",
                     label=self.unitLabels()[idx], addSpace=False,
                    items=['Si','Ge'],
                    valueType=int, orientation="horizontal")
        self.show_at(self.unitFlags()[idx], box1) 


        #widget index 1 
        idx += 1 
        box1 = gui.widgetBox(boxa) 
        oasysgui.lineEdit(box1, self, "MILLER_INDEX_H",
                     label=self.unitLabels()[idx], addSpace=False,
                    valueType=int, validator=QIntValidator(), orientation="horizontal")
        self.show_at(self.unitFlags()[idx], box1) 
        
        #widget index 2 
        idx += 1 
        box1 = gui.widgetBox(boxa) 
        oasysgui.lineEdit(box1, self, "MILLER_INDEX_K",
                     label=self.unitLabels()[idx], addSpace=False,
                    valueType=int, validator=QIntValidator(), orientation="horizontal")
        self.show_at(self.unitFlags()[idx], box1) 
        
        #widget index 3 
        idx += 1 
        box1 = gui.widgetBox(boxa) 
        oasysgui.lineEdit(box1, self, "MILLER_INDEX_L",
                     label=self.unitLabels()[idx], addSpace=False,
                    valueType=int, validator=QIntValidator(), orientation="horizontal")
        self.show_at(self.unitFlags()[idx], box1)         

        #widget index 7 
        idx += 1 
        box1 = gui.widgetBox(boxb) 
        gui.label(box1, self, "Stiffness matrix C:\n%(C_MATRIX_STR)s\nCompliance matrix S:\n%(S_MATRIX_STR)s", orientation="horizontal")
        self.show_at(self.unitFlags()[idx], box1) 

        
        gui.rubber(self.controlArea)

    def unitLabels(self):
         return ['Crystal:','h Miller index','k Miller index','l Miller index']


    def unitFlags(self):
         return ['True',          'True',       'True', 'True','True']

    def calculate(self):
        xtal = ['Si','Ge']
        xtal = xtal[self.CRYSTAL_MATERIAL]
        hkl = [self.MILLER_INDEX_H,self.MILLER_INDEX_K,self.MILLER_INDEX_L]
        S,C = compute_elastic_matrices(hkl,xtal)
        datadict = {}
        datadict['xtal'] = xtal
        datadict['hkl'] = hkl
        datadict['S_matrix'] = S 
        datadict['C_matrix'] = C 

        self.S_MATRIX_STR = np.array2string(S,precision=2)
        self.C_MATRIX_STR = np.array2string(C,precision=2)


        self.send("elastic_tensor_data",datadict)

    def defaults(self):
         self.resetSettings()
         #self.set_deformation()
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
