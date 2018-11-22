This diretory is not needed by Oasys. 

It contains some tools used to create the widgets.

For each widget you should: 

1) create a <widget name>.json file with the values of the widget
fields. These are the input parameters that will be displayed in the
widget. Give the default values. 

2) A file .json.ext with the titles of each field and the mapping flags.

3) run: 
python create_widget.py <widget name>.py

if it runs succesfully, you get <widget name>.py 

3) copy/move the <widget name>.py to the desired directory under ../widgets/

4) Create/copy an image with the icon and place it in the ./icons
directory
