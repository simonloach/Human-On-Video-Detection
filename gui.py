import PySimpleGUI as sg
import sys
import re
import os
from main import vid
import cv2

class GUI:
    
    layout = [[sg.Text('Progress made')],
          [sg.ProgressBar(1000, orientation='h', size=(20, 20), key='progbar')],
          [sg.Cancel()]]
    layout2 = [[sg.Text('Document to open')],
                [sg.Text('Input File', justification='r', size=(15,1)),sg.Input(key='input_file'), sg.FileBrowse(target='input_file')],
                [sg.Text('Output Folder:', justification='r', size=(15,1)),sg.Input(key='output_folder'), sg.FolderBrowse(target='output_folder')],
                [sg.Open(), sg.Cancel()]]

    def __init__(self):
        window = sg.Window('My Script', self.layout2)
        while True:
            event, values = window.read(close=True)
            print(values)
            print(event)
            if event == sg.WIN_CLOSED:
                break
            elif event == 'Cancel':
                break

            if event=='Open':
                if os.path.isfile(values['input_file']):
                    if values['input_file'].lower().endswith(('.mpg', '.mp4')):
                        self.path_to_file = values['input_file']
                        self.path_to_save = values['output_folder']   
                        vid(values['input_file'], values['output_folder'])
                        sg.popup(f"Saved file in {values['output_folder']}")
                    else:
                        sg.popup('Wrong input file extension')
                else:
                    sg.popup("Not a valid input file path")     
        window.close()


GUI()

