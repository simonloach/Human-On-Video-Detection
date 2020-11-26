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

with open('models/coco.names', 'r') as f:
    CLASSES = f.read().splitlines()


def vid(pathToFile):
    frame_index = 0
    frames_output = []
    if DEBUG >= 0:
        print(f"[INFO] Reading file {pathToFile}")
    cap = cv2.VideoCapture(pathToFile)
    folder_name = str(datetime.datetime.now()).replace(
        " ", "_")[:19].replace(":", "_")
    try:
        os.mkdir("output/" + folder_name)
        if DEBUG >= 0: print(f"Created folder /{folder_name}")
    except:
        if DEBUG >= 0:print(f"Can't create folder named {folder_name}")

    while(True):
        frame_index += 1
        ret, frame = cap.read()
        if not ret:
            if DEBUG >= 0:
                print('[INFO] Last frame')
            break

        if frame_index == 1:
            height, width, _ = frame.shape
            if DEBUG >= 0:
                start = time.time()

        if (frame_index-1) % jump == 0:
            globals().update(analyse(frame, height, width))
            print(boxes)
        print(boxes)
        if "FIRST_BOXES" in globals(): putBoxes(frame, boxes, class_ids, confidences, indexes)

        if (frame_index % 10 == 0):
            if (DEBUG >= 0):
                print("[INFO] ", frame_index, " frames analysed, speed=",
                      10/(time.time() - start), "fps", "  "*40)
                start = time.time()
                if DEBUG > 1:
                    progress(frame_index, cap.get(
                        cv2.CAP_PROP_FRAME_COUNT), "Processing video file")
            sg.OneLineProgressMeter('Progressmeter', frame_index, cap.get(cv2.CAP_PROP_FRAME_COUNT), 'key')

        if OUTPUT_PHOTOS:
            cv2.imwrite(f"output/{folder_name}/{frame_index}.png", frame)
        if OUTPUT_VIDEO:
            frames_output.append(frame)
    writeVideo(frames_output, folder_name, (width,height))
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
    try:
        layerOutputs = net.forward(output_layers_names)
    except:
        print('failed')

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


def saveVideo(list_of_frames):
    framesize = (list_of_frames[0].shape[1], list_of_frames[0].shape[0])
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video = cv2.VideoWriter(
        'output.avi', cv2.VideoWriter_fourcc(*'DIVX'), 30, framesize)
    for frame in list_of_frames:
        video.write(frame)
        cv2.imshow("test", frame)
        cv2.waitKey(3)
    video.release()


def progress(count, total, status=''):
    bar_len = 60
    filled_len = int(round(bar_len * count / float(total)))

    percents = round(100.0 * count / float(total), 1)
    bar = '=' * filled_len + '-' * (bar_len - filled_len)

    sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', status))
    sys.stdout.flush()


def writeVideo(frames_list, folder, size):
    out = cv2.VideoWriter(f"output/{folder}.avi", cv2.VideoWriter_fourcc(*'XVID'), 15, size)
    for frame in frames_list:   
        out.write(frame)
    out.release()
