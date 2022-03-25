import numpy as np
#from Avoidance_v0 import *
from djitellopy import tello
import cv2
#import os
#from skimage.transform import resize
#import tensorflow as tf
from keras.models import load_model
from PyTorch import layers
#from layers import BilinearUpSampling2D
import time

# 드론 카메라 혹은 웹캠으로 받은 영상 depth estimation 하기

# Visualization
import matplotlib.pyplot as plt

#plasma = plt.get_cmap('plasma')

drone = True
#tf.compat.v1.disable_eager_execution()
#global model
#graph = tf.compat.v1.get_default_graph()

if drone:
    me = tello.Tello()
    me.connect()
    print(me.get_battery())
    me.streamon()
#    me.takeoff()
#    me.send_rc_control(0,0,0,0)

def DepthNorm(x, maxDepth):
    return maxDepth / x

def predict(model, images, minDepth=10, maxDepth=1000, batch_size=2):
    
    # Support multiple RGBs, one RGB image, even grayscale 
    if len(images.shape) < 3: images = np.stack((images,images,images), axis=2)
    if len(images.shape) < 4: images = images.reshape((1, images.shape[0], images.shape[1], images.shape[2]))
    # Compute predictions
    predictions = model.predict(images, batch_size=batch_size)
    # Put in expected range
    return np.clip(DepthNorm(predictions, maxDepth=maxDepth), minDepth, maxDepth) / maxDepth

def depth(me, img, time0):
    model_path = 'nyu.h5'
    # Custom object needed for inference and training
    custom_objects = {'BilinearUpSampling2D': layers.BilinearUpSampling2D, 'depth_loss_function': None}
    model = load_model(model_path, custom_objects=custom_objects, compile=False)
    #model.summary()

    time1 = time.time()
    print("gap1", time1-time0)
    img = me.get_frame_read().frame
    img = cv2.resize(img, (64*4,48*4))
    cv2.imshow("streaming", img)
    cv2.waitKey(1)

    input1 = np.clip(np.asarray(img, dtype=float) / 255, 0, 1)
    # Compute results
    #input2 = np.clip(np.asarray(np.flip(img,axis=1), dtype=float) / 255, 0, 1)
    output1 = predict(model, input1)
    time2 = time.time()
    print("gap2", time2-time1)
    img = me.get_frame_read().frame
    img = cv2.resize(img, (64 * 4, 48 * 4))
    cv2.imshow("streaming", img)
    cv2.waitKey(1)
    #output2 = predict(model, input2)
    rescaled1 = output1[0,:,:,0]
    rescaled1 = rescaled1 - np.min(rescaled1)
    rescaled1 = rescaled1 / np.max(rescaled1)
    rescaled1 =  cv2.resize(rescaled1, (img.shape[1],img.shape[0]))
    time3 = time.time()
    print("gap3", time3-time2)
    return rescaled1, time3
'''
    rescaled2 = np.flip(output2[0,:,:,0],axis=1)
    rescaled2 = rescaled2 - np.min(rescaled2)
    rescaled2 = rescaled2 / np.max(rescaled2)
    rescaled2 =  cv2.resize(rescaled2, (img.shape[1],img.shape[0]))
    rescaled = (rescaled1+rescaled2)/2
    return rescaled
'''
def mk_area(me, depth_, time3):
    img = me.get_frame_read().frame
    img = cv2.resize(img, (64 * 4, 48 * 4))
    cv2.imshow("streaming", img)
    cv2.waitKey(1)
    time4 = time.time()
    print(time4-time3)
    anum = 3 # 5보단 3일때가 더 정확한 정보를 제공해주는듯
    depths = []
    height = depth_.shape[0]
    width = depth_.shape[1]
    h_gap = int((height+(anum-1))/anum)
    w_gap = int((width+(anum-1))/anum)
    row_st = 0
    for i in range(anum):
        col_st = 0
        row_e = min(row_st + h_gap, height)
        for j in range(anum):
            col_e = min(col_st + w_gap, width)
            depths.append(depth_[row_st:row_e, col_st:col_e])
            col_st = col_e
        row_st = row_e
    area_avg = []
    area = []
    for i in range(len(depths)): area_avg.append(np.average(depths[i]))
    for i in range(anum):
        area.append(area_avg[i*anum:(i+1)*anum])
        #print(area_max[i*anum:(i+1)*anum])
    area = np.array(area)
    print(area)
    print("#############################")  
    return area, time4

import time
start = 0
end = 0
if not drone: cap = cv2.VideoCapture(0)
n=0
while n<5:
    yaw = me.get_yaw()
    #y = -int(yaw/4) if yaw != 0 else 0
#    me.send_rc_control(0,5,0,0)
    if drone: img = me.get_frame_read().frame
    print(me.get_yaw())
    if not drone: ret, img = cap.read()
    img = cv2.resize(img, (64*4,48*4))
    cv2.imshow("streaming", img)
    cv2.waitKey(1)
    start = time.time()
    print(start-end)
    depth_ = depth(me, img)
    end = time.time()
    print(end-start)
    print(me.get_yaw())
    if drone: img = me.get_frame_read().frame
    if not drone: ret, img = cap.read()
    img = cv2.resize(img, (64*4,48*4))
    #depth__ = (1000/model.predict(np.expand_dims(img, axis=0)))/1000
    #depth_ = (plasma(depth__[0,:,:,0])[:,:,:3] * 255).astype('uint8')
    #area = mk_area(me, depth_*255)

    cv2.imshow("streaming", img) #(window name, mat)
    #cv2.imshow("depth", depth_) #(window name, mat)
    cv2.waitKey(1)
    n+=1
    # 이미지를 받아서 depth를 계산하고 이미지를 출력하는데 0.2~0.3초 정도(평균 0.24초) 걸림

#me.send_rc_control(0, 0, 0, 0)
#me.land()
