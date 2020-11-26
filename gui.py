import PySimpleGUI as sg
import sys
import re
import os
from main import vid


class GUI:
    
    layout = [[sg.Text('Progress made')],
          [sg.ProgressBar(1000, orientation='h', size=(20, 20), key='progbar')],
          [sg.Cancel()]]

    def __init__(self):
        while True:
            event, values = sg.Window('My Script',
                    [[sg.Text('Document to open')],
                    [sg.In(), sg.FileBrowse()],
                    [sg.Open(), sg.Cancel()]]).read(close=True)
            try:
                print(values)
                if os.path.isfile(values[0]):
                    if values[0].lower().endswith(('.mpg', '.mp4')):
                        self.path_to_file = values[0]
                        vid(self.path_to_file)
                        sg.popup("Saved file in 'output/' folder")
                        break       
                else:
                    sg.popup("Wrong path or file format")

            except TypeError:
                sg.popup("Wrong path type")
GUI()