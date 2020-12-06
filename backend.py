import os
import cv2
import numpy as np
import datetime
import time
import PySimpleGUI as sg
import math

def timing(f):
    '''
        Wrapper used for checking calculating the time to call a function. It prints the call time into console.


    Parameters:
        f (function): Function that the call time will be measured.

    '''
    def wrap(*args, **kwargs):
        time1 = time.time()
        ret = f(*args, **kwargs)
        time2 = time.time()
        print('{:s} function took {:.3f} ms'.format(f.__name__, (time2-time1)*1000.0))

        return ret
    return wrap


def loadVideo(input_file_path, output_path):
    '''
    Main function that loads video file, splits it into frames and forwards them into the analyse()
    function. Then depending on the result and frequency of our analysis function putBoxes() can be
    called to put the results on the output video. The video is later saved with saveVideo() to the
    'output_path' folder.


    Parameters:
        input_file_path (str): Path to the input video file.
        output_path (str): Path to the output video folder.
    '''

    FRAME_LIST = []
    capture = cv2.VideoCapture(input_file_path)
    frame_id = 1

    while True:
        retrived, frame = capture.read()
        if not retrived:
            break
        if frame_id==1:
            height, width, _ = frame.shape
        if (frame_id) % SKIP == 0:
            globals().update(analyse(frame, height, width, model))
            sg.OneLineProgressMeter('Progressmeter', frame_id, capture.get(cv2.CAP_PROP_FRAME_COUNT), 'key')
        if FIRST_SUCCESS_DETECTION:
            putBoxes(frame, 
                    boxes,
                    class_ids,
                    confidences,
                    indexes)
        frame_id = frame_id + 1
        FRAME_LIST.append(frame)

    capture.release()
    saveVideo(FRAME_LIST, output_path, (width, height))


def analyse(frame, height, width, model):
    '''
    Returns a dictionary as a result of neural network object detection. 


    Parameters:
        frame (cv::OutputArrayOfArrays): Image to be analysed.
        height (int): Height of analysed image.
        width (int): Width of analysed image.
        model (cv::dnn::Net): Model of a pre-trained neural network.


    Returns:
        dictionary: Dictionary with results of the analysis.
    '''
    blob = cv2.dnn.blobFromImage(
        frame, 1/255, (416, 416), (0, 0, 0), swapRB=True, crop=False)
    model.setInput(blob)
    output_layers_names = model.getUnconnectedOutLayersNames()
    time.sleep(0.5)
    layer_outputs = model.forward(output_layers_names)

    boxes = []
    confidences = []
    class_ids = []

    for output in layer_outputs:
        for detection in output:
            scores = detection[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > 0.5:
                center_x = int(detection[0]*width)
                center_y = int(detection[1]*height)
                w = int(detection[2]*width)
                h = int(detection[3]*height)
                x = int(center_x - w/2)
                y = int(center_y - h/2)

                boxes.append([x, y, w, h])
                confidences.append((float(confidence)))
                class_ids.append(class_id)
    
    if len(boxes)>0:
        indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)
        return {'GO_ON':False,
                'FIRST_SUCCESS_DETECTION':True,
                'boxes': boxes,
                'class_ids':class_ids,
                'confidences':confidences,
                'indexes':indexes}
    else:
        return {'GO_ON':False}


def putBoxes(frame, boxes, class_ids, confidences, indexes):
    '''
    Moddifies frame with boxes drawn around detected objects. 


    Parameters:
        cropped_frame (cv::OutputArrayOfArrays): Video in a form of list of frames.
        weights_3d (numpy:array): Array filled with values between 0.0-1.0. For more info check generateColorWeights()
    '''
    final_boxes=[]
    final_labels=[]
    person_counter = 0
    global ONCE
    for i in indexes.flatten():
        if (not ONLY_PERSON) or (str(CLASSES[class_ids[i]]) == 'person'):
            person_counter += 1
            x, y, w, h = boxes[i]
            if x<0: x=0
            if y<0: y=0
            color = calculateColor(frame[y:y+h,x:x+w], COLOR_WEIGHTS_3D)
            final_boxes.append({"pt1":(x,y),
                                "pt2":(x+w, y+h),
                                "color":color,
                                "thickness":2
                                })
            final_labels.append({"text":str(CLASSES[class_ids[i]]) + " " + str(round(confidences[i], 2)),
                                "org":(x, y+20),
                                "fontFace": cv2.FONT_HERSHEY_DUPLEX,
                                "fontScale":0.8,
                                "color":color,
                                "thickness":2
                                })
    for box in final_boxes:
        cv2.rectangle(frame, box['pt1'], box['pt2'], box['color'], thickness=1)
    for label in final_labels:
        cv2.putText(frame, label['text'], label['org'], label['fontFace'], label['fontScale'], label['color'], thickness=1)
    cv2.putText(frame, "people count: {:12}".format(str(person_counter)), (50, 50), cv2.FONT_HERSHEY_DUPLEX, 1, (255,20,147), 2)


def calculateColor(cropped_frame, weights_3d):
    '''
    Calculates the dominant colour within the cropped_frame multiplied by weights matrix that favours shape of a person instead of background.


    Parameters:
        cropped_frame (cv::OutputArrayOfArrays): Video in a form of list of frames.
        weights_3d (numpy:array): Array filled with values between 0.0-1.0. For more info check generateColorWeights()


    Returns:
        tuple: Tuple that holds the dominant colour - (R,G,B).
    '''

    array_frame = np.array(cropped_frame)

    try:
        array_frame = cv2.resize(array_frame, weights_3d.shape[::-1][1:4])
        transformed_frame = (array_frame*weights_3d).astype(int)
    except ValueError:
        print('Value Error in calculate colour')
    RGB = np.sum(transformed_frame, axis=(0,1))
    return tuple(255 if index == np.argmax(RGB) else 0 for index in range(3))

   
def generateColorWeights(height, width, translation_parameter=0.1):
    '''
    Returns width x height array with weights for dominant colour calculation. It allows for elimination of background colors.


    Parameters:
        height (int): Height of image that the mask will be applied to.
        width (int): Width of image that the mask will be applied to.
        translation_parameter(float): How much above the center of the matrix should our weights be focused (equal to 1.0)


    Returns:
        np.array: 3D array made from 2D arrays stacked on the third axis. Values are in range from 0.0-1.0
        
    '''
    center = (int(height/2), int(width/2))
    translate_above =  int(height*translation_parameter)
    list_2d = [[1 for _ in range(width)] for _ in range(height)]
    for y in range(width):
        for x in range(height):
            if (((x-center[0]+translate_above)**2 )/( (height/2)**2 ) + ((y-center[1])**2)/((width/2)**2) <= 0.5):
                list_2d[x][y]=(max(height/2, width/2)-math.sqrt(((center[0]-x-translate_above)**2)+((center[1]-y)**2))) / max(height/2, width/2)
            else:
                list_2d[x][y]=0
    array_2d = np.array(list_2d)
    array_3d = np.dstack((array_2d,array_2d,array_2d))
    return array_3d


def saveVideo(frames_list, save_folder, size):
    '''
    Saves video into the save folder.


    Parameters:
        frames_list (list): Video in a form of list of frames.
        save_folder (str): Path to the save folder ex. "C:/Users/zz/yy/ss"
        size (tuple): Size of our frames which also means resolution of a saved video.
    '''


    file_name = str(datetime.datetime.now()).replace(" ", "_")[:19].replace(":", "_")
    print(f"{save_folder}/{file_name}.avi")
    out = cv2.VideoWriter(f"{save_folder}/{file_name}.avi", cv2.VideoWriter_fourcc(*'XVID'), 15, size)
    for frame in frames_list:   
        out.write(frame)
    out.release()


MODEL = 'yolov3'
PATH = os.getcwd()
WEIGHTS = f'{PATH}/models/{MODEL}/{MODEL}.weights'.replace("\\", "/")
CFG = f'{PATH}/models/{MODEL}/{MODEL}.cfg'.replace("\\", "/")
SKIP = 5
ONLY_PERSON = True
FIRST_SUCCESS_DETECTION = False

CLASSES=[]
ONCE = True

model = cv2.dnn.readNet(WEIGHTS, CFG)
model.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)

with open('models/coco.names', 'r') as f:
    CLASSES = f.read().splitlines()

COLOR_WEIGHTS_3D = generateColorWeights(416,416)
