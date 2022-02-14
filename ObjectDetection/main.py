import numpy as np
import cv2
import torch
from PIL import Image
import tflite
import tensorflow as tf
import argparse
import requests
import json
import djitellopy as tello
import os
os.environ["CUDA_VISIBLE_DEVICES"] = '0'

global img, str
global results, labels
global flag_y, flag_e

# 푸시 알림 구현 정보(서버키, 토큰)
serverToken = "AAAAPLrhMZw:APA91bHWU8_gHlBY6a8c-NC0MJVzA-zEj7ZsusRb_-fsQRH5PJYlG3JSs9257c1gCrM2iktf-jKG3Rs-bCsX4lgFVJLG6_WFGxUYv7q9eWmZTZpqjRn_iic9gHW0WREWbfKCNjTOJc2X"
deviceToken = "ecSMotavQpqD5FuX7E2biS:APA91bF9NrPSS-Ixzf-4XnTcZmHONLKz6qbJgVErXWeV2hWxTD_hgcNRiGf2X0BCor4srYGC01ubL0Aa5egu_oRcI8Cg5yIC9d87IyUXIapU7pZ_sLAvnWTIF7zbgqQufc40JSxeBtWe"

headers = {
        'Content-Type': 'application/json',
        'Authorization': 'key=' + serverToken,
      }
# 알림 메시지 정보
body = {
          'notification': {'title': '🚨 화재 발생 🚨',
                            'body': '🔥 화재가 발생하였습니다. 즉시 출동 바랍니다. 🔥'
                            },
          'to':
              deviceToken,
          'priority': 'high',
        #   'data': dataPayLoad,
        }

def load_labels(filename):
    with open(filename, 'r') as f:
        return [line.strip() for line in f.readlines()]

def efficientNet(image):
    global str, flag_e

    # EfficientNet-lite0 코드 부분
    if __name__ == '__main__':
        parser = argparse.ArgumentParser()
        parser.add_argument(
            '-i',
            '--image',
            default='./img.jpg',
            help='image to be classified')
        parser.add_argument(
            '-m',
            '--model_file',
            default='./model.tflite',
            help='.tflite model to be executed')
        parser.add_argument(
            '-l',
            '--label_file',
            default='./labels.txt',
            help='name of file containing labels')
        parser.add_argument(
            '--input_mean',
            default=127.5, type=float,
            help='input_mean')
        parser.add_argument(
            '--input_std',
            default=127.5, type=float,
            help='input standard deviation')
        parser.add_argument(
            '--num_threads', default=None, type=int, help='number of threads')
        parser.add_argument(
            '-e', '--ext_delegate', help='external_delegate_library path')
        parser.add_argument(
            '-o',
            '--ext_delegate_options',
            help='external delegate options, \
                format: "option1: value1; option2: value2"')

        args = parser.parse_args()

        ext_delegate = None
        ext_delegate_options = {}

        # parse extenal delegate options
        if args.ext_delegate_options is not None:
            options = args.ext_delegate_options.split(';')
            for o in options:
                kv = o.split(':')
                if (len(kv) == 2):
                    ext_delegate_options[kv[0].strip()] = kv[1].strip()
                else:
                    raise RuntimeError('Error parsing delegate option: ' + o)

        # load external delegate
        if args.ext_delegate is not None:
            print('Loading external delegate from {} with args: {}'.format(
                args.ext_delegate, ext_delegate_options))
            ext_delegate = [
                tflite.load_delegate(args.ext_delegate, ext_delegate_options)
            ]

        interpreter = tf.lite.Interpreter(
            model_path=args.model_file,
            experimental_delegates=ext_delegate,
            num_threads=args.num_threads)
        interpreter.allocate_tensors()

        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()

        # check the type of the input tensor
        floating_model = input_details[0]['dtype'] == np.float32

        # NxHxWxC, H:1, W:2
        height = input_details[0]['shape'][1]
        width = input_details[0]['shape'][2]


    image = Image.open(args.image).resize((width, height))

    # add N dim
    input_data = np.expand_dims(image, axis=0)

    if floating_model:
        input_data = (np.float32(input_data) - args.input_mean) / args.input_std

    interpreter.set_tensor(input_details[0]['index'], input_data)

    interpreter.invoke()

    output_data = interpreter.get_tensor(output_details[0]['index'])
    results = np.squeeze(output_data)

    top_k = results.argsort()[-5:][::-1]
    labels = load_labels(args.label_file)

    for i in top_k:
        if floating_model:
            print('{:08.6f}: {}'.format(float(results[i]), labels[i]))
        else:
            print('{:08.6f}: {}'.format(float(results[i] / 255.0), labels[i]))

    if float(results[0]) > float(results[1]):
        str = '{:03.2f}: {}'.format(float(results[0] / 255.0), labels[0])
    else:
        str = '{:03.2f}: {}'.format(float(results[1] / 255.0), labels[1])

    if float(results[1] / 255.0) >= 0.6:
        flag_e=True
    else:
        flag_e=False


# Load model from PyTorch Hub
model = torch.hub.load('ultralytics/yolov5',
                        'yolov5s')  # Path to custom model weights

#'custom','./best.pt'

# initialize drone
#me = tello.Tello()
#me.connect()

# Initiate video stream
#me.streamon()

cap = cv2.VideoCapture(0)

# YOLOv5 실행 횟수
cnt=0
noti_flag = False # 일회성 푸시 알림 flag

flag_e = False # 푸시 알림 조건 - efficientnet 정확도
flag_y = False # 푸시 알림 조건 - yolo 정확도

str = "Testing . . ."

# YOLOv5s 코드
while True:
    cnt += 1
    #img = me.get_frame_read().frame
    #img1 = me.get_frame_read().frame
    _, img1=cap.read()
    _, img = cap.read()
    cv2.imwrite("./img.jpg", img1)

    img_detect = model(img)  # default YOLOv5 size=460, custom model was trained with 416
    img_show = img_detect.render()
    img_detect.print()
    cv2.imshow("yolo",img_show[0])

    if len(img_detect.xyxy[0]) > 0:
        if float(img_detect.xyxy[0][0][4]) >= 0.9:
            flag_y = True
        else:
            flag_y = False

    if cnt==50:
        efficientNet(img1) # efficientNet 실행
        cnt=0

    if noti_flag==False :
        if flag_y or flag_e:
            response = requests.post("https://fcm.googleapis.com/fcm/send", headers=headers, data=json.dumps(body))
            print(response.json())

            noti_flag = True # 푸시 알림 전송 완료

    cv2.waitKey(1)
