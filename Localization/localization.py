import numpy as np
# from Avoidance_v0 import *
# import os
# from skimage.transform import resize
# import tensorflow as tf
from keras.models import load_model
from layers import BilinearUpSampling2D
import math
from exDepth_v1 import *
import time
import cv2
import torch
from PIL import Image
#import tflite
import tensorflow as tf
import argparse
import requests
import json
import djitellopy as tello
import firebase_admin
from firebase_admin import credentials
from firebase_admin import storage
from firebase_admin import db
from uuid import uuid4

global img
global results, labels
global flag_y, flag_e

# 푸시 알림 구현 정보(서버키, 토큰)
serverToken = "###"
deviceToken = "###"

headers = {
        'Content-Type': 'application/json',
        'Authorization': 'key=' + serverToken,
      }
# 알림 메시지 정보
body = {
          'notification': {'title': '🚨 조난자 발견 🚨',
                            'body': '📢 조난자를 발견하였습니다. 즉시 출동 바랍니다.',
                            },
          'to':
              deviceToken,
          'priority': 'high',
        #   'data': dataPayLoad,
        }

# 파이어베이스 업로드 정보
PROJECT_ID = "project-000"
# my project id

cred = credentials.Certificate("./###.json")  # (키 이름 ) 부분에 본인의 키이름을 적어주세요.
default_app = firebase_admin.initialize_app(cred, {'storageBucket': f"{PROJECT_ID}.appspot.com",
                                                   'databaseURL' : "https://###.firebaseio.com/"})



# 데이터베이스에 드론 시작점 업로드
dir = db.reference('startpoint')
dir.update({'latitude':37.566903})
dir.update({'longitude':126.947944})


# 조난자 위치 업로드 변수
degree = 0.00
direction = 0
distance = 0.00
dir2 = db.reference('survivor')

# 버킷은 바이너리 객체의 상위 컨테이너이다. 버킷은 Storage에서 데이터를 보관하는 기본 컨테이너이다.
bucket = storage.bucket()  # 기본 버킷 사용

def fileUpload(file):
    blob = bucket.blob('image_store/' + file)  # 저장한 사진을 파이어베이스 storage의 image_store라는 이름의 디렉토리에 저장
    # new token and metadata 설정
    new_token = uuid4()
    metadata = {"firebaseStorageDownloadTokens": new_token}  # access token이 필요하다.
    blob.metadata = metadata

    # upload file
    blob.upload_from_filename(filename='./image_store/' + file,
                              content_type='image/png')  # 파일이 저장된 주소와 이미지 형식(jpeg도 됨)
    # debugging hello
    print("upload")
    print(blob.public_url)

def load_labels(filename):
    with open(filename, 'r') as f:
        return [line.strip() for line in f.readlines()]



drone = True
# tf.compat.v1.disable_eager_execution()
# global model
# graph = tf.compat.v1.get_default_graph()

if drone:
    me = tello.Tello()
    # me.RESPONSE_TIMEOUT = 17
    me.connect()
    print(me.get_battery())
    me.streamon()

inter = 0
end = 0
if not drone: cap = cv2.VideoCapture(0)
n = 0
model_path = 'nyu.h5'
# Custom object needed for inference and training
custom_objects = {'BilinearUpSampling2D': BilinearUpSampling2D, 'depth_loss_function': None}
model_depth = load_model(model_path, custom_objects=custom_objects, compile=False)
# model.summary()

# Load model from PyTorch Hub
model = torch.hub.load('./yolov5', 'yolov5s', source='local')
# model = torch.hub.load('ultralytics/yolov5', 'yolov5s')
model.classes = [0]  # person

mode = 0
Time = 0

grid = 1
row = 4 * grid
col = 4 * grid
turn = 1
cur_turn = 0
speed = 10
pos_y = 0
pos_x = 0
leave = True
start = 0
# YOLOv5 실행 횟수
cnt_yolo=0

noti_flag = False # 일회성 푸시 알림 flag

flag_e = False # 푸시 알림 조건 - efficientnet 정확도
flag_y = False # 푸시 알림 조건 - yolo 정확도

#str = "Testing . . ."

# 이미지 저장 형식 (firebase)
filename = "_fire.png"
# 이미지 업로드 횟수
cnt_image=0


# 이미지 업로드 횟수
while True:

    if drone: img = me.get_frame_read().frame
    if not drone: ret, img = cap.read()
    width = 64 * 4 * 2
    height = 48 * 4 * 2
    img = cv2.resize(img, (width, height))
    depth_ = depth(model_depth, img)
    area = mk_area(depth_)

    img_detect = model(img)  # default YOLOv5 size=460, custom model was trained with 416
    x1 = 0
    x2 = 0
    y1 = 0
    y2 = 0
    cx = 0
    cy = 0
    if len(img_detect.xyxy[0]) > 0:
        x1 = int(img_detect.xyxy[0][0][0])
        y1 = int(img_detect.xyxy[0][0][1])
        x2 = int(img_detect.xyxy[0][0][2])
        y2 = int(img_detect.xyxy[0][0][3])
        cx = (x1 + x2) / 2
        cy = (y1 + y2) / 2

    depth_tot = 0
    count = 0
    xgap = x2 - x1
    ygap = y2 - y1
    for i in range(x1 + int(xgap / 5 * 2), x2 - int(xgap / 5 * 2)):
        for j in range(y1 + int(ygap / 5), y2 - int(ygap / 5)):
            depth_tot += depth_[j, i]
            count += 1
    avg_depth = 0


    # take off drone
    if leave:
        me.takeoff()
        me.send_rc_control(0, 0, 0, 0)
        leave = False
    
    me.send_rc_control(0, speed, 0, 0)

    if start == 0: start = time.time()
    inter = time.time()

    font = cv2.FONT_HERSHEY_PLAIN
    # if person is detected
    if count > 0:
        avg_depth = depth_tot / count;
        print("depth is ", depth_tot / count)
        dist_y = 0.012 * (avg_depth * 100 + 50) * (avg_depth * 100 + 50) + 100
        # dist_x1 = dist_y * abs(cx-width/2)/cy
        dist_x2 = dist_y * abs(cx - width / 2) / (width / 2) * math.tan(math.radians(41.3))
        # az = math.atan(dist_x1/dist_y)
        az2 = math.atan(dist_x2 / dist_y)
        # dist = math.sqrt(dist_y*dist_y + dist_x1*dist_x1)#dist_y/math.cos(az)
        dist2 = math.sqrt(dist_y * dist_y + dist_x2 * dist_x2)  # dist_y/math.cos(az2)
        # txt_dist = "distance "+str(int(dist))
        # txt_az = "az "+str(int(math.degrees(az)))
        txt_dist2 = "distance " + str(int(dist2))
        txt_az2 = "az " + str(int(math.degrees(az2)))

        # org_dist = (10, 10)
        # org_az = (10, 40)
        org_dist2 = (10, 10)
        org_az2 = (10, 25)
        org_app = (10, 40)
        # cv2.putText(img, txt_dist, org_dist, font, 1, (0, 255, 0), 2)
        # cv2.putText(img, txt_az, org_az, font, 1, (0, 255, 0), 2)
        yaw = me.get_yaw()
        print("=================================")
        print("cx", cx)
        if cx >= width / 2:
            degree = yaw+(int(math.degrees(az2)))
        else:
            degree = yaw-(int(math.degrees(az2)))
        print("yaw", yaw)
        print("az2", az2)
        print("degree", degree)
        degree = (degree + 360) % 360
        print("degree", degree)
        direction_ = int(degree / 30 + 0.5)
        print("direction_", direction_)

        ## FireBase 코드
        # 조난자 위치 업로드
        direction = direction_ # 시 계산한 변수
        distance = int(dist2/100) # 거리 계산한 변수



        txt_app = str(me.get_yaw())+"yaw "+str(direction_) + " HOUR," + str(degree) + " DEGREE"
        cv2.putText(img, txt_dist2, org_dist2, font, 1, (0, 100, 255), 2)
        cv2.putText(img, txt_az2, org_az2, font, 1, (0, 100, 255), 2)
        cv2.putText(img, txt_app, org_app, font, 1, (0, 100, 255), 2)
    end = time.time()
    if mode == 0:
        pos_y = int(Time*speed)
    elif mode == 1 or mode == 3:
        pos_x = int((cur_turn+1)*2 + Time*speed)
    else:
        pos_y = int(row/grid*speed - Time*speed)

    if (mode == 0) and (Time >= row):
        me.rotate_clockwise(90)
        mode = 1
        inter = end
        cur_turn += 1
    elif (mode == 1) and (Time >= col):
        me.rotate_clockwise(90)
        mode = 2
        inter = end
    elif (mode == 2) and (Time >= row):
        me.rotate_counter_clockwise(90)
        mode = 3
        inter = end
    elif (mode == 3) and (Time >= col):
        me.rotate_counter_clockwise(90)
        mode = 0
        inter = end
        # cur_turn += 1
    if cur_turn == turn:
        break

    txt_pos = "Drone Pos: (" + str(pos_x) + ", " + str(pos_y) + ")"
    org_pos = (10, height - 10)
    #cv2.putText(img, txt_pos, org_pos, font, 1, (0, 0, 255), 2)
    img_show = img_detect.render()
    img_detect.print()
    cv2.imshow("yolo", img_show[0])

    cv2.imshow("streaming", img)
    # cv2.imshow("streaming", img) #(window name, mat)
    cv2.imshow("depth", depth_)  # (window name, mat)
    cv2.waitKey(1)
    n += 1

    cnt_yolo += 1

    if len(img_detect.xyxy[0]) > 0:
        if float(img_detect.xyxy[0][0][4]) >= 0.5:
            flag_y = True
        else:
            flag_y = False

    if noti_flag==False :
        if flag_y:
            response = requests.post("https://fcm.googleapis.com/fcm/send", headers=headers, data=json.dumps(body))
            print(response.json())
            noti_flag = True # 푸시 알림 전송 완료
    else:
        if cnt_yolo%8 == 0 and cnt_image < 5:
            cv2.imwrite("./image_store/"+str(cnt_image)+filename, img)
            fileUpload(str(cnt_image)+filename)  # 사진 파일 파이어베이스 업로드

            dir2.update({'degree': degree})
            dir2.update({'direction': direction})
            dir2.update({'distance': distance})

            print(cnt_image)
            cnt_image += 1


me.send_rc_control(0, 0, 0, 0)
me.land()
