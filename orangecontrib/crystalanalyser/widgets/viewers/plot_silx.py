from PyQt5 import QtWidgets
from orangewidget import gui
from oasys.widgets import widget, gui as oasysgui
import numpy as np

from silx.gui.plot.PlotWindow import PlotWindow


class OWPlotSilx(widget.OWWidget):
    name = "Plot using Silx"
    id = "OWPlotSilx"
    description = ""
    icon = "icons/Unknown.svg"
    author = ""
    maintainer_email = ""
    priority = 2
    category = ""
    keywords = ["list", "of", "keywords"]
    inputs = [{"name": "oasysaddontemplate-data",
                "type": np.ndarray,
                "doc": "",
                "handler": "do_plot" }]


    def __init__(self):
        super().__init__()

        gui.label(self.controlArea, self, "PUT YOUR INPUT FORM HERE")

        self.figure_canvas = None

    def do_plot(self, custom_data):
        x = custom_data[0,:]
        y = custom_data[-1,:]
        x.shape = -1
        y.shape = -1
        title = "top"
        xtitle = "X"
        ytitle = "Y"
        print (x,y)

        plot = PlotWindow(roi=True, control=True, position=True)
        plot.setDefaultPlotLines(False)
        plot.setActiveCurveColor(color='darkblue')
        plot.addCurve(x, y, title, symbol='o', color='blue') #'+', '^',
        plot.setGraphXLabel(xtitle)
        plot.setGraphYLabel(ytitle)
        plot.setDrawModeEnabled(True, 'rectangle')
        plot.setZoomModeEnabled(True)

        if self.figure_canvas is not None:
            self.mainArea.layout().removeWidget(self.figure_canvas)

        self.figure_canvas = plot

        self.mainArea.layout().addWidget(self.figure_canvas)

        gui.rubber(self.mainArea)

if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    ow = OWPlotSilx()
    a = np.array([
        [  8.47091837e+04,  8.57285714e+04,   8.67479592e+04, 8.77673469e+04,] ,
        [  1.16210756e+12,  1.10833975e+12,   1.05700892e+12, 1.00800805e+12]
        ])
    ow.do_plot(a)
    ow.show()
    app.exec_()
    ow.saveSettings()
