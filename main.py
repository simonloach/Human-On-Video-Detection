import cv2
import numpy as np
import time
import os
import datetime
import sys
import PySimpleGUI as sg

from config import *


Once = True
CLASSES = []
PATH = os.getcwd()
WEIGHTS = f'{PATH}/models/{MODEL}/{MODEL}.weights'
CFG = f'{PATH}/models/{MODEL}/{MODEL}.cfg'

net = cv2.dnn.readNet(WEIGHTS, CFG)
net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)

with open('models/coco.names', 'r') as f:
    CLASSES = f.read().splitlines()


def vid(pathToFile, save_folder):
    frame_index = 0
    frames_output = []
    cap = cv2.VideoCapture(pathToFile)
    while(True):
        frame_index += 1
        ret, frame = cap.read()
        if not ret:
            break

        if frame_index == 1:
            start = time.time()
            copy = frame
            height, width, _ = frame.shape

        if (frame_index-1) % jump == 0:
            globals().update(analyse(copy, height, width))
        #print(globals())
        if "FIRST_BOXES" in globals(): putBoxes(copy, boxes, class_ids, confidences, indexes)

        if (frame_index % 10 == 0):
            if (DEBUG >= 0):
                print(frame_index)
            sg.OneLineProgressMeter('Progressmeter', frame_index, cap.get(cv2.CAP_PROP_FRAME_COUNT), 'key')
        if OUTPUT_VIDEO:
            frames_output.append(copy)
    cap.release()
    writeVideo(frames_output, save_folder, (width,height))
    if DEBUG >= 0:
        print("[DONE] Finished processing!")
    return True


def analyse(frame, height, width):
    global net
    img = frame
    blob = cv2.dnn.blobFromImage(
        img, 1/255, (416, 416), (0, 0, 0), swapRB=True, crop=False)
    net.setInput(blob)

    output_layers_names = net.getUnconnectedOutLayersNames()
    print("pre forward")
    layerOutputs = net.forward(output_layers_names)
    print("after forward")

    boxes = []
    confidences = []
    class_ids = []

    for output in layerOutputs:
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
    if len(boxes) > 0:
        indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)

        if DEBUG > 1:
            print(
                f"BOXES:\n\t {boxes} \n\t len {len(boxes)} \n\t type {type(boxes)}")
            print(
                f"INDEXES:\n\t {indexes} \n\t len {len(indexes)}\n\t type {type(indexes)}\n\t shape {indexes.shape}")
            print(
                f"CONFIDENCES:\n\t {confidences} \n\t len {len(confidences)}\n\t type {type(confidences)}")
            print("="*30)
        return {'GO_ON':True,
                'FIRST_BOXES':True,
                'frame': img,
                'boxes': boxes,
                'class_ids':class_ids,
                'confidences':confidences,
                'indexes':indexes}
    else:
        return {'GO_ON':False}


def putBoxes(img, boxes, class_ids, confidences, indexes):
    person_counter = 0
    font = cv2.FONT_ITALIC
    for i in indexes.flatten():
        if (not ONLY_PERSON) or (str(CLASSES[class_ids[i]]) == 'person'):
            x, y, w, h = boxes[i]
            color = (255, 255, 255)
            label = str(CLASSES[class_ids[i]])
            confidence = str(round(confidences[i], 2))
            person_counter += 1
            if PUT_RECTANGLE:
                cv2.rectangle(img, (x, y), (x+w, y+h), color, 2)
            if PUT_LABEL:
                cv2.putText(img, label + " " + confidence,
                            (x, y+20), font, 0.8, (255, 255, 255), 2)
    if PUT_COUNTER:
        cv2.putText(img, "people count: {:12}".format(
            str(person_counter)), (50, 50), font, 1, (0, 255, 0), 4)


def calculateColor(frame, x, y, w, h):  # TODO
    frame = frame[int(x-w/2)+2:int(x+w/2)-2, int(y-h/2)+2:int(y+h/2)-2]
    global Once
    if Once:
        print("Shape: ", frame.shape)
        print("Frame:", frame[255][255])
        Once = False
    return (255, 255, 255)


def writeVideo(frames_list, save_folder, size):
    file_name = str(datetime.datetime.now()).replace(" ", "_")[:19].replace(":", "_")
    out = cv2.VideoWriter(f"{save_folder}/{file_name}.avi", cv2.VideoWriter_fourcc(*'XVID'), 15, size)
    for frame in frames_list:   
        out.write(frame)
    out.release()

while True:
    vid('C:/Users/MrThe/OneDrive/Pulpit/vids/sample.mpg', 'C:/Users/MrThe/OneDrive/Pulpit/vids')