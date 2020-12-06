import PySimpleGUI as sg
import os
from backend import loadVideo

class GUI:
    '''
    A class to represent our GUI

    Attributes
    ----------
    layout : list
        Layout of our GUI main window filled with PySimpleGUI objects.
    '''
    layout = [[sg.Text('Document to open')],
                [sg.Text('Input File', justification='r', size=(15,1)),sg.Input(key='input_file'), sg.FileBrowse(target='input_file')],
                [sg.Text('Output Folder:', justification='r', size=(15,1)),sg.Input(key='output_folder'), sg.FolderBrowse(target='output_folder')],
                [sg.Open(), sg.Cancel()]]

    def __init__(self):
        '''
        Constructs all the necessary windows for our GUI to work.
        Checks if paths and file extensions are correct.
        If all fine passes the path to loadVideo() function.
        If object detection succeded displays popup that confirms.


        '''
        window = sg.Window('My Script', self.layout)
        while True:
            event, values = window.read(close=True)
            if event == sg.WIN_CLOSED:
                break
            elif event == 'Cancel':
                break

            if event=='Open':
                if os.path.isfile(values['input_file']):
                    if values['input_file'].lower().endswith(('.mpg', '.mp4')):
                        self.path_to_file = values['input_file']
                        self.path_to_save = values['output_folder']
                        loadVideo(values['input_file'], values['output_folder'])
                        sg.popup(f"Saved file in {values['output_folder']}")
                    else:
                        sg.popup('Wrong input file extension')
                else:
                    sg.popup("Not a valid input file path")     
        window.close()
GUI()