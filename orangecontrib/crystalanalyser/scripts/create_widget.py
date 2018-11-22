import sys
import os


def read_json(json_name):
    json_text = open(json_name).read()
    json_dict = eval(json_text)
    json = sorted(json_dict.items(),
                  key=lambda x: json_text.index('"{}"'.format(x[0])))
    json_lowercase = json
    return json_lowercase


def create_settings(json):
    settings = ""
    for name, value in json:
        if isinstance(value, str):
            settings += '    {} = Setting("{}")\n'.format(name, value)
        elif isinstance(value, list):
            settings += '    {} = Setting({})\n'.format(name, value[0])
        else:
            settings += '    {} = Setting({})\n'.format(name, value)
    return settings

def create_calc_args_default(json):
    settings = ""
    i = -1
    for name, value in json:
        i += 1
        if isinstance(value, str):
            settings += '{}="{}"'.format(name, value).rstrip('\n')
        elif isinstance(value, list):
            settings += '{}={}'.format(name, value[0]).rstrip('\n')
        else:
            settings += '{}={}\n'.format(name, value).rstrip('\n')
        if i < (len(json)-1):
           settings += ','
    return settings

def create_calc_args(json):
    calc_args = ""
    i = -1
    for name, value in json:
        i += 1
        calc_args += '{}=self.{}'.format(name, name)
        if i < (len(json)-1):
           calc_args += ','
    return calc_args


def create_controls(json):
    controls = ""
    controls += '        box0 = gui.widgetBox(self.controlArea, " ",orientation="horizontal") \n'
    controls += '        #widget buttons: compute, set defaults, help\n'
    controls += '        gui.button(box0, self, "Compute", callback=self.compute)\n'
    controls += '        gui.button(box0, self, "Defaults", callback=self.defaults)\n'
    controls += '        gui.button(box0, self, "Help", callback=self.get_doc)\n'
    controls += '        self.process_showers()\n'


    controls += '        box = gui.widgetBox(self.controlArea, " ",orientation="vertical") \n'
    idx = -1
    controls += '        \n'
    controls += '        \n'
    controls += '        idx = -1 \n'


    for name, value in json:
        idx += 1
        controls += '        \n'
        controls += '        #widget index '+str(idx)+' \n'
        controls += '        idx += 1 \n'
        controls += '        box1 = gui.widgetBox(box) \n'
        if isinstance(value, list):
            controls += list_template.format(name=name,values=str(value[1:]))
        else:
            controls += line_edit_templates[type(value)].format(name=name)

        controls += '        self.show_at(self.unitFlags()[idx], box1) \n'

    return controls


def main():
    json_name = sys.argv[1]
    base = os.path.splitext(json_name)[0]
    py_name =  base + ".py"

    if os.path.exists(py_name):
        print("file overwritten: "+py_name+"\n")
    else:
        print("file written: "+py_name+"\n")

    json = read_json(json_name)
    widget_name = base
    widget_class_name = widget_id_name = base.replace(" ", "")
    settings = create_settings(json)
    controls = create_controls(json)
    calc_args = create_calc_args(json)
    calc_args_default = create_calc_args_default(json)

    f = open(json_name+'.ext')
    lines = f.readlines()
    f.close()

    labels = lines[0]
    flags = lines[1]
    open(py_name, "wt").write(widget_template.format_map(vars()))



control_template = """        gui.{}(box1, self, "{{name}}",
                     label=self.unitLabels()[idx], addSpace=True"""


str_template = control_template.format("lineEdit") + ")\n"

int_template = control_template.format("lineEdit") + """,
                    valueType=int, validator=QIntValidator())
"""

float_template = control_template.format("lineEdit") + """,
                    valueType=float, validator=QDoubleValidator())
"""

line_edit_templates = {str: str_template, int: int_template,
                       float: float_template}

list_template = control_template.format("comboBox") + """,
                    items={values},
                    valueType=int, orientation="horizontal")
"""



widget_template = """import sys
import numpy as np
from PyQt5.QtGui import QIntValidator, QDoubleValidator
from PyQt5.QtWidgets import QApplication, QSizePolicy
from orangewidget import gui
from orangewidget.settings import Setting
from orangewidget import widget
from oasys.widgets import widget as oasyswidget, gui as oasysgui
import orangecanvas.resources as resources
import sys,os

class OW{widget_class_name}(oasyswidget.OWWidget):
    name = "{widget_name}"
    id = "orange.widgets.data{widget_id_name}"
    description = "Application to compute..."
    icon = "icons/{widget_class_name}.png"
    author = "create_widget.py"
    maintainer_email = "srio@esrf.eu"
    priority = 10
    category = ""
    keywords = ["oasysaddontemplate", "{widget_class_name}"]
    outputs = [{{"name": "oasysaddontemplate-data",
                "type": np.ndarray,
                "doc": "transfer numpy arrays"}},
               # another possible output
               # {{"name": "oasysaddontemplate-file",
               #  "type": str,
               #  "doc": "transfer a file"}},
                ]

    # widget input (if needed)
    #inputs = [{{"name": "Name",
    #           "type": type,
    #           "handler": None,
    #           "doc": ""}}]

    want_main_area = False

{settings}

    def __init__(self):
        super().__init__(self)

        self.runaction = widget.OWAction("Compute", self)
        self.runaction.triggered.connect(self.compute)
        self.addAction(self.runaction)

{controls}
        gui.rubber(self.controlArea)

    def unitLabels(self):
         return {labels}

    def unitFlags(self):
         return {flags}

    def compute(self):
        dataArray = OW{widget_class_name}.calculate_external_{widget_class_name}({calc_args})

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
        filename1 = os.path.join(home_doc,'{widget_class_name}'+'.txt')
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
    def calculate_external_{widget_class_name}({calc_args_default}):
        print("Inside calculate_external_{widget_class_name}. ")

        # A MERE EXAMPLE
        a = np.array([
        [  8.47091837e+04,  8.57285714e+04,   8.67479592e+04, 8.77673469e+04,] ,
        [  1.16210756e+12,  1.10833975e+12,   1.05700892e+12, 1.00800805e+12]
        ])

        return a


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = OW{widget_class_name}()
    w.show()
    app.exec()
    w.saveSettings()
"""

main()

