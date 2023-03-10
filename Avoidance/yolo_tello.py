import torch
import cv2
import os
import math
import numpy as np
from keras.models import load_model
import sys
sys.path.append('/home/hong/DingDone_final/Avoidance/DenseDepth')
#from .. import layers
from layers import BilinearUpSampling2D
from exDepth import *
from djitellopy import tello


# Model
# model = torch.hub.load('ultralytics/yolov5', 'yolov5s')
model = torch.hub.load('../DenseDepth/yolov5', 'yolov5s', source='local')
model.classes = [0]
width = 64*8*2
height = 48*8*2
depth_list = []
dist_list = []

me = tello.Tello()
me.connect()
print(me.get_battery())
me.streamon()


while True:
    frame = me.get_frame_read().frame
    frame = cv2.resize(frame, (width, height))
    #print(np.shape(frame))
    #img = model(frame)
    
    #img = cv2.imread(path, cv2.IMREAD_COLOR)
    #img = cv2.resize(img, (width, height))
    # Inference
    results = model(frame)
    #depth_ = depth(img)

    for j in range(len(results.xyxy[0])):
        x1 = int(results.xyxy[0][j][0])
        y1 = int(results.xyxy[0][j][1])
        x2 = int(results.xyxy[0][j][2])
        y2 = int(results.xyxy[0][j][3])
        cx = (x1 + x2) / 2

        print(x1, y1, x2, y2)
        gap = 3
        gap_x = int((x2-x1)/gap)
        gap_y = int((y2-y1)/gap)
        s = int(gap/2)
        print(gap_x, gap_y)
        bw = x2-x1
        
        dist = 60*np.shape(frame)[1] / (bw * 2 * math.tan(math.radians(41.3)))
        dist_x = dist * abs(cx - width / 2) / (width / 2) * math.tan(math.radians(41.3))
        #ddxx = cx-width/2 if cx>width/2 else width/2
        #dist_x = 0.01 * dist * ddxx / (width / 2) * math.tan(math.radians(41.3))

        az = math.degrees(math.atan(dist_x / dist))
        print("az", az)
        #az = (az + 360) % 360
        hour = int(az / 30 + 0.5)
        if cx < width / 2 and hour > 0:
            hour = 12 - hour
        #if cx >= width / 2:
        #    degree = yaw+(int(math.degrees(az)))
        #else:
        #    degree = yaw-(int(math.degrees(az)))
        

        dist2 = math.sqrt(dist * dist + dist_x * dist_x)  # direction시 방향으로 dist2(m)
        
        # results.pandas().xyxy[0]
        txt = "distance: "+str(int(dist)) + "cm"
        txt_north = f"{round(dist)}cm to the North"
        txt_clck = f"{round(dist2)}cm to the {hour} o'clock direction"
        xpos, ypos = x1, y1 - 30
        if y1 - 50 <= 0: ypos = y2 - 30
        elif ypos > height: 
            ypos = y1 - 30
            xpos = x2 + 30
            #if xpos >= width: xpos = x1 - 60
        cv2.rectangle(frame, (xpos, ypos), (xpos+420, ypos-20),  (255, 80, 80), thickness=-1)
        cv2.rectangle(frame, (xpos, ypos), (xpos+250, ypos-40),  (255, 80, 80), thickness=-1)
        #cv2.putText(frame, txt, (xpos, ypos), cv2.FONT_HERSHEY_PLAIN, 1.5, (255, 255, 255), 2) #print("dist: ", dist, "cm")
        cv2.putText(frame, txt_north, (xpos, ypos-20), cv2.FONT_HERSHEY_PLAIN, 1.5, (255, 255, 255), 2) #print("dist: ", dist, "cm")
        cv2.putText(frame, txt_clck, (xpos, ypos-0), cv2.FONT_HERSHEY_PLAIN, 1.5, (255, 255, 255), 2) #print("dist: ", dist, "cm")
        dist_list.append(dist)
        #f.write(str(depth_mean) + ',' + str(dist) + '\n')
    #cv2.imwrite('./output/{5d}.png'.format(i), results)
    #cv2.imwrite("./output/1.jpg", results)
    #results.save()
    #results.show()


    img_show = results.render()
    #results.print()
    
    cv2.imshow("distance", img_show[0])
    cv2.waitKey(1)
