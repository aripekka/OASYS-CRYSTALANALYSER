import sys
import numpy as np
from PyQt5.QtCore import QLocale
from PyQt5.QtGui import QIntValidator, QDoubleValidator
from PyQt5.QtWidgets import QApplication, QSizePolicy
from orangewidget import gui
from orangewidget.settings import Setting
from orangewidget import widget
from oasys.widgets import widget as oasyswidget, gui as oasysgui
import orangecanvas.resources as resources
import sys,os

from pyTTE import takagitaupin
from xraylib import Crystal_GetCrystalsList

import signal

class StopComputationInterrupt(Exception):
    pass

def stopcomputationhandler(signumber,frame):
    raise StopComputationInterrupt()

class OWpyTTE(oasyswidget.OWWidget):
    name = "pyTTE"
    id = "orange.widgets.pyTTE"
    description = "1D Takagi-Taupin solver for bent crystals."
    icon = "icons/pytte_icon.png"
    author = "Ari-Pekka Honkanen"
    maintainer_email = "honkanen.ap@gmail.com"
    priority = 10
    category = ""
    keywords = ["crystalanalyser", "pyTTE"]
    outputs = [{"name": "pyTTE_data",
                "type": np.ndarray,
                "doc": "transfer numpy arrays(temporary)"},
               # another possible output
               # {"name": "oasysaddontemplate-file",
               #  "type": str,
               #  "doc": "transfer a file"},
                ]

    inputs = [{"name": "pyTTE_deformation_data",
                "type": dict,
                "doc": "",
                "handler": "handle_deformation" },
                ]

    want_main_area = False

    CRYSTAL_MATERIAL = Setting(32)
    MILLER_INDEX_H = Setting(1)
    MILLER_INDEX_K = Setting(1)
    MILLER_INDEX_L = Setting(1)
    THICKNESS = Setting(300.0)
    DEBYEWALLER = Setting(1.0)
    ASYMMETRY = Setting(0.0)
    POLARIZATION = Setting(0)

    DEFORMATION_FIELD = Setting(None)
    DEFORMATION_DESCRIPTION = Setting('NONE')
    DEFORMATION_ANISOTROPIC = Setting(False)

    SCAN_TYPE = Setting(0)
    E0 = Setting(6.0)
    BRAGGTH = Setting(20.0)
    FROM = Setting(-10.0)
    TO = Setting(30.0)
    NPOINTS = Setting(150)
    MIN_INT_STEP = Setting(1e-10)

    DUMP_TO_FILE = Setting(0)
    FILE_NAME = Setting("tmp.dat")

    def __init__(self):
        super().__init__()

        self.runaction = widget.OWAction("Compute", self)
        self.runaction.triggered.connect(self.compute)
        self.addAction(self.runaction)

        boxparent = gui.widgetBox(self.controlArea, "PyTTE - 1D Takagi-Taupin solver",orientation="horizontal") 
        boxa = gui.widgetBox(boxparent, "Crystal parameters",orientation="vertical") 
        boxb = gui.widgetBox(boxparent, "Simulation parameters",orientation="vertical") 
        self.plotbox = gui.widgetBox(boxparent, " ",orientation="vertical") 
        self.plotbox.layout().addWidget(oasysgui.plotWindow())

        doublevalidator = QDoubleValidator()
        doublevalidator.setLocale(QLocale('C')) #This fixes the problem with decimal sepator by forcing it to '.'
        doublevalidator.setNotation(QDoubleValidator.ScientificNotation)

        self.DEFORMATION_FIELD = None
        self.DEFORMATION_DESCRIPTION = 'NONE'
        self.DEFORMATION_ANISOTROPIC = False

        ####################
        #CRYSTAL PARAMETERS#
        ####################

        idx = -1 
        
        #widget index 0 
        idx += 1 
        box1 = gui.widgetBox(boxa) 
        gui.comboBox(box1, self, "CRYSTAL_MATERIAL",
                     label=self.unitLabelsa()[idx], addSpace=False,
                    items=Crystal_GetCrystalsList(),
                    valueType=int, orientation="horizontal")
        self.show_at(self.unitFlagsa()[idx], box1) 
        
        #widget index 1 
        idx += 1 
        box1 = gui.widgetBox(boxa) 
        oasysgui.lineEdit(box1, self, "MILLER_INDEX_H",
                     label=self.unitLabelsa()[idx], addSpace=False,
                    valueType=int, validator=QIntValidator(), orientation="horizontal")
        self.show_at(self.unitFlagsa()[idx], box1) 
        
        #widget index 2 
        idx += 1 
        box1 = gui.widgetBox(boxa) 
        oasysgui.lineEdit(box1, self, "MILLER_INDEX_K",
                     label=self.unitLabelsa()[idx], addSpace=False,
                    valueType=int, validator=QIntValidator(), orientation="horizontal")
        self.show_at(self.unitFlagsa()[idx], box1) 
        
        #widget index 3 
        idx += 1 
        box1 = gui.widgetBox(boxa) 
        oasysgui.lineEdit(box1, self, "MILLER_INDEX_L",
                     label=self.unitLabelsa()[idx], addSpace=False,
                    valueType=int, validator=QIntValidator(), orientation="horizontal")
        self.show_at(self.unitFlagsa()[idx], box1)         

        #widget index 4 
        idx += 1 
        box1 = gui.widgetBox(boxa) 
        oasysgui.lineEdit(box1, self, "THICKNESS",
                     label=self.unitLabelsa()[idx], addSpace=True,
                    valueType=float, validator=doublevalidator)
        self.show_at(self.unitFlagsa()[idx], box1) 

        #widget index 5 
        idx += 1 
        box1 = gui.widgetBox(boxa) 
        oasysgui.lineEdit(box1, self, "DEBYEWALLER",
                     label=self.unitLabelsa()[idx], addSpace=True,
                    valueType=float, validator=doublevalidator)
        self.show_at(self.unitFlagsa()[idx], box1) 

        #widget index 6 
        idx += 1 
        box1 = gui.widgetBox(boxa) 
        oasysgui.lineEdit(box1, self, "ASYMMETRY",
                     label=self.unitLabelsa()[idx], addSpace=True,
                    valueType=float, validator=doublevalidator)
        self.show_at(self.unitFlagsa()[idx], box1) 


        #widget index 7 
        idx += 1 
        box1 = gui.widgetBox(boxa) 
        gui.comboBox(box1, self, "POLARIZATION",
                     label=self.unitLabelsa()[idx], addSpace=True,
                    items=['Sigma', 'Pi'],
                    valueType=int, orientation="horizontal")
        self.show_at(self.unitFlagsa()[idx], box1) 

        #widget index 7 
        idx += 1 
        box1 = gui.widgetBox(boxa) 
        gui.label(box1, self, "Deformation:\n%(DEFORMATION_DESCRIPTION)s", orientation="horizontal")
        self.show_at(self.unitFlagsa()[idx], box1) 

        
        idx = -1 

        #widget index 0 
        idx += 1 
        box1 = gui.widgetBox(boxb) 
        gui.comboBox(box1, self, "SCAN_TYPE",
                     label=self.unitLabelsb()[idx], addSpace=True,
                    items=['Angle (arc sec)', 'Energy (meV)'],
                    valueType=int, orientation="horizontal")
        self.show_at(self.unitFlagsb()[idx], box1) 

        #widget index 0 
        idx += 1 
        box1 = gui.widgetBox(boxb) 
        oasysgui.lineEdit(box1, self, "E0",
                     label=self.unitLabelsb()[idx], addSpace=True,
                    valueType=float, validator=doublevalidator)
        self.show_at(self.unitFlagsb()[idx], box1) 

        #widget index 0 
        idx += 1 
        box1 = gui.widgetBox(boxb) 
        oasysgui.lineEdit(box1, self, "BRAGGTH",
                     label=self.unitLabelsb()[idx], addSpace=True,
                    valueType=float, validator=doublevalidator)
        self.show_at(self.unitFlagsb()[idx], box1) 

        
        #widget index 0 
        idx += 1 
        box1 = gui.widgetBox(boxb) 
        oasysgui.lineEdit(box1, self, "FROM",
                     label=self.unitLabelsb()[idx], addSpace=True,
                    valueType=float, validator=doublevalidator)
        self.show_at(self.unitFlagsb()[idx], box1) 
        
        #widget index 1 
        idx += 1 
        box1 = gui.widgetBox(boxb) 
        oasysgui.lineEdit(box1, self, "TO",
                     label=self.unitLabelsb()[idx], addSpace=True,
                    valueType=float, validator=doublevalidator)
        self.show_at(self.unitFlagsb()[idx], box1) 
        
        #widget index 2 
        idx += 1 
        box1 = gui.widgetBox(boxb) 
        oasysgui.lineEdit(box1, self, "NPOINTS",
                     label=self.unitLabelsb()[idx], addSpace=True,
                    valueType=int, validator=QIntValidator())
        self.show_at(self.unitFlagsb()[idx], box1) 

        #widget index 3 
        idx += 1 
        box1 = gui.widgetBox(boxb) 
        oasysgui.lineEdit(box1, self, "MIN_INT_STEP",
                     label=self.unitLabelsb()[idx], addSpace=True,
                    valueType=float, validator=doublevalidator)
        self.show_at(self.unitFlagsb()[idx], box1) 
        
        
        #widget index 5 
        idx += 1 
        box1 = gui.widgetBox(boxb) 
        gui.comboBox(box1, self, "DUMP_TO_FILE",
                     label=self.unitLabelsb()[idx], addSpace=True,
                    items=['Yes', 'No'],
                    valueType=int, orientation="horizontal")
        self.show_at(self.unitFlagsb()[idx], box1) 
        
        #widget index 6 
        idx += 1 
        box1 = gui.widgetBox(boxb) 
        gui.lineEdit(box1, self, "FILE_NAME",
                     label=self.unitLabelsb()[idx], addSpace=True)
        self.show_at(self.unitFlagsb()[idx], box1) 

        box0 = gui.widgetBox(boxb, " ",orientation="horizontal") 
        #widget buttons: compute, set defaults, help
        gui.button(box0, self, "Compute", callback=self.compute)
        gui.button(box0, self, "Defaults", callback=self.defaults)
        gui.button(box0, self, "Help", callback=self.get_doc)
        self.process_showers()


        gui.rubber(self.controlArea)

    def unitLabelsa(self):
         return ['Crystal:','h Miller index','k Miller index','l Miller index',u'Crystal thickness (µm)','Debye-Waller factor','Asymmetry (deg)\nSet 90 for symmetric Laue','Polarization','Deformation']

    def unitFlagsa(self):
         #Function to define whether widgets are visible or not
         return ['not self.DEFORMATION_ANISOTROPIC','not self.DEFORMATION_ANISOTROPIC','not self.DEFORMATION_ANISOTROPIC','not self.DEFORMATION_ANISOTROPIC','self.DEFORMATION_FIELD == None','True','True','True','True']


    def unitLabelsb(self):
         return ['Scan type','Photon energy (keV)','Bragg angle (deg)','Scan low limit','Scan high limit','Number of points','Minimum integration step',      'Dump to file','File name']


    def unitFlagsb(self):
         #Function to define whether widgets are visible or not
         return ['True', 'self.SCAN_TYPE == 0', 'self.SCAN_TYPE == 1' ,   'True',          'True',       'True',            'True','True',        'self.DUMP_TO_FILE == 0']


    def handle_deformation(self,defdict):
        self.DEFORMATION_FIELD = defdict
        if defdict == None:
            self.DEFORMATION_DESCRIPTION = '\nNONE'
            self.DEFORMATION_ANISOTROPIC = False
        else:
            if defdict['isotropy'] == 'isotropic':
                self.DEFORMATION_ANISOTROPIC = False
                self.DEFORMATION_DESCRIPTION = '\nIsotropy: ' + defdict['isotropy'] + '\n' +\
                  'Crystal thickness: ' + str(defdict['thickness']) + ' um\n' +\
                  'Bending radius (meridional): ' + str(defdict['bending_radii'][0]) + ' m\n' +\
                  'Bending radius (sagittal): ' + str(defdict['bending_radii'][1]) + ' m\n' +\
                  "Poisson's ratio: " + str(defdict['nu'])
            else:
                self.DEFORMATION_ANISOTROPIC = True
                hkl = defdict['hkl']
                self.DEFORMATION_DESCRIPTION = '\nIsotropy: ' + defdict['isotropy'] + '\n' +\
                  'Crystal material: ' + defdict['xtal'] + '\n'+\
                  'Reflection:  ('+str(hkl[0])+','+str(hkl[1])+','+str(hkl[2])+') \n' +\
                  'Crystal thickness: ' + str(defdict['thickness']) + ' um\n' +\
                  'Bending radius (meridional): ' + str(defdict['bending_radii'][0]) + ' m\n' +\
                  'Bending radius (sagittal): ' + str(defdict['bending_radii'][1]) + ' m'

    def compute(self):
        #dataArray = OWfunctions1D.calculate_external_functions1D(FROM=self.FROM,TO=self.TO,NPOINTS=self.NPOINTS,FUNCTION_NAME=self.FUNCTION_NAME,CUSTOM=self.CUSTOM,DUMP_TO_FILE=self.DUMP_TO_FILE,FILE_NAME=self.FILE_NAME)


        scanvector = np.linspace(self.FROM,self.TO,self.NPOINTS)

        if self.SCAN_TYPE == 0:
            scantype = 'angle'
            constant = self.E0
            plot_xtitle = '$\Delta \\theta$ (arcsec)'
        elif self.SCAN_TYPE == 1:
            scantype = 'energy'
            constant = self.BRAGGTH
            plot_xtitle = '$\Delta E$ (meV)'
        if self.POLARIZATION == 0:
            polarization = 'sigma'
        elif self.POLARIZATION == 1:
            polarization = 'pi'

        if self.DEFORMATION_FIELD == None:
            ujac = None
            thickness = self.THICKNESS
            xtal = Crystal_GetCrystalsList()[self.CRYSTAL_MATERIAL]
            hkl = [self.MILLER_INDEX_H,self.MILLER_INDEX_K,self.MILLER_INDEX_L]
        else:
            ujac = self.DEFORMATION_FIELD['jacobian']
            thickness = self.DEFORMATION_FIELD['thickness']
            if self.DEFORMATION_FIELD['isotropy'] == 'anisotropic':
                xtal = self.DEFORMATION_FIELD['xtal']
                hkl = self.DEFORMATION_FIELD['hkl']
            else:
                xtal = Crystal_GetCrystalsList()[self.CRYSTAL_MATERIAL]
                hkl = [self.MILLER_INDEX_H,self.MILLER_INDEX_K,self.MILLER_INDEX_L]


        #Temporarily disable KeyboardInterruption
        original_sigint_handler = signal.signal(signal.SIGINT,stopcomputationhandler)
        try:
            R,T=takagitaupin(scantype,scanvector,constant,polarization,xtal,hkl,self.ASYMMETRY,
                             thickness,ujac,self.DEBYEWALLER,self.MIN_INT_STEP)

            # if fileName == None:
            #     print("No file to send")
            # else:
            #     self.send("oasysaddontemplate-file",fileName)

            plot_title = xtal+'('+str(hkl[0])+','+str(hkl[1])+','+str(hkl[2])+') '
            if T[0] == -1:
                plot_title = plot_title + 'Bragg case '
                plot_ytitle = 'Reflectivity'
            else:
                plot_title = plot_title + 'Laue case '
                plot_ytitle = 'Transmitted/reflected intensity (rel. to incident)'
            if self.SCAN_TYPE == 0:
                plot_title = plot_title + 'at ' +str(constant) + ' keV'
            else:
                plot_title = plot_title + 'at ' +str(constant) + ' deg'

            self.send("pyTTE_data",(np.array([scanvector,R,T]).T))
            self.plot_curves(scanvector,R,T,plot_xtitle,plot_ytitle,plot_title)
        except StopComputationInterrupt:
            print('\nKeyboard interrupt received. Computation cancelled.')
        finally:
            signal.signal(signal.SIGINT,original_sigint_handler)

    def plot_curves(self,dataX,dataY,dataY2,xtitle='x',ytitle='y',title='title'):

        self.plotbox.layout().removeItem(self.plotbox.layout().itemAt(0))

        plot_canvas = oasysgui.plotWindow()

        plot_canvas.addCurve(dataX, dataY,legend='1')
        plot_canvas.addCurve(dataX, dataY2,legend='2')

        plot_canvas.resetZoom()
        #plot_canvas.setXAxisAutoScale(True)
        #plot_canvas.setYAxisAutoScale(True)
        plot_canvas.setLimits(dataX.min(),dataX.max(),0,np.max([np.max(dataY),np.max(dataY2)]))
        plot_canvas.setGraphGrid(False)

        plot_canvas.setXAxisLogarithmic(False)
        plot_canvas.setYAxisLogarithmic(False)
        plot_canvas.setGraphXLabel(xtitle)
        plot_canvas.setGraphYLabel(ytitle)
        plot_canvas.setGraphTitle(title)

        self.plotbox.layout().addWidget(plot_canvas)



    def defaults(self):
         self.resetSettings()
         #self.compute()
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
    w = OWpyTTE()
    w.show()
    app.exec()
    w.saveSettings()
