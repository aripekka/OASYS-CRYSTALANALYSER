from PyQt5 import QtWidgets

from orangewidget import gui
from orangewidget.settings import Setting
from oasys.widgets import widget, gui as oasysgui

import numpy as np

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas



class OWPlotSimple(widget.OWWidget):
    name = "Plot Simple"
    id = "OWPlotSimple"
    description = ""
    icon = "icons/plot_simple.png"
    author = ""
    maintainer_email = ""
    priority = 1
    category = ""
    keywords = ["list", "of", "keywords"]
    inputs = [{"name": "oasysaddontemplate-data",
                "type": np.ndarray,
                "doc": "",
                "handler": "do_plot" },
                ]


    input_field = Setting(10.0)

    def __init__(self):
        super().__init__(self)

        box = oasysgui.widgetBox(self.controlArea, "Input Form", orientation="vertical")

        oasysgui.lineEdit(box, self, "input_field", "Example Input field", valueType=float)
        gui.button(box, self, "Do Plot", callback=self.button_action)


        self.figure_canvas = None

    def do_plot(self, custom_data):
        x = custom_data[0,:]
        y = custom_data[-1,:]
        x.shape = -1
        y.shape = -1
        fig = plt.figure()
        plt.plot(x,y,linewidth=1.0, figure=fig)
        plt.grid(True)

        if self.figure_canvas is not None:
            self.mainArea.layout().removeWidget(self.figure_canvas)

        self.figure_canvas = FigureCanvas(fig)

        self.mainArea.layout().addWidget(self.figure_canvas)

        gui.rubber(self.mainArea)

    def button_action(self):
        a = np.array([
            [  8.47091837e+04,  8.57285714e+04,   8.67479592e+04, 8.77673469e+04,] ,
            [  self.input_field,  self.input_field,   self.input_field, self.input_field]
            ])

        self.do_plot(a)

if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    ow = OWPlotSimple()
    a = np.array([
        [  8.47091837e+04,  8.57285714e+04,   8.67479592e+04, 8.77673469e+04,] ,
        [  1.16210756e+12,  1.10833975e+12,   1.05700892e+12, 1.00800805e+12]
        ])
    ow.do_plot(a)
    ow.show()
    app.exec_()
    ow.saveSettings()
