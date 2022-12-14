import torch
import cv2
from keras.models import load_model
import sys
sys.path.append('/home/hong/DingDone_final/Avoidance/DenseDepth')
#from .. import layers
from layers import BilinearUpSampling2D
from exDepth import *



# Model
# model = torch.hub.load('ultralytics/yolov5', 'yolov5s')
model = torch.hub.load('../DenseDepth/yolov5', 'yolov5s', source='local')
model.classes = [0] # detect only person
videopath = '../../Localization/a_person_moving_2.mp4'
cap = cv2.VideoCapture(videopath)

#depthpath = '/home/hong/DingDone_final/Avoidance/DenseDepth/kitti.h5'
#custom_objects = {'BilinearUpSampling2D': BilinearUpSampling2D, 'depth_loss_function': None}
#model_depth = load_model(depthpath, custom_objects=custom_objects, compile=False)

while True:
    retval, frame = cap.read()
    #cv2.imshow('img', frame)
    frame = cv2.resize(frame, (64*8, 48*8))
    depth_ = depth(frame)
    img_detect = model(frame)
    img_show = img_detect.render()
    img_detect.print()
    #depth_ = cv2.resize(depth_, (64, 48))
    #img_show = cv2.resize(img_show, (64, 48))
    #cv2.imshow("depth", depth_)

    if len(img_detect.xyxy[0]) > 0:
        x1 = int(img_detect.xyxy[0][0][0])
        y1 = int(img_detect.xyxy[0][0][1])
        x2 = int(img_detect.xyxy[0][0][2])
        y2 = int(img_detect.xyxy[0][0][3])
        print(f"bounding box size (height: {y2-y1}, width: {x2-x1})")
        for y in range(y1, y2+1):
            for x in range(x1, x2+1):
                print(round(depth_[y][x]*10, 2), end = " ")
            print()

    cv2.imshow("yolo", img_show[0])
    cv2.waitKey(1)