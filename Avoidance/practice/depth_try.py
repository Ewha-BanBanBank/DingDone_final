
  
import cv2
#activate myWincv conda env for this
from keras.models import load_model
from layers import BilinearUpSampling2D
from utils import predict, load_images, display_images
from matplotlib import pyplot as plt
import numpy as np
import time
# Custom object needed for inference and training
custom_objects = {'BilinearUpSampling2D': BilinearUpSampling2D, 'depth_loss_function': None}

print('Loading model...')
model_path = "nyu.h5"
# Load model into GPU / CPU
model = load_model(model_path, custom_objects=custom_objects, compile=False)
model.summary()
print('\nModel loaded ({0}).'.format(model_path))
cap = cv2.VideoCapture(0)
def depth(img):
	input1 = np.clip(np.asarray(img, dtype=float) / 255, 0, 1)
	# Compute results
	input2 = np.clip(np.asarray(np.flip(img,axis=1), dtype=float) / 255, 0, 1)
	#op = predict(model, np.array([input1,input2]))
	#output1,output2 = op[0],op[1]
	output1 = predict(model, input1)
	output2 = predict(model, input2)
	#cv2_imshow(outputs[0,:,:,0])
	rescaled1 =output1[0,:,:,0]
	rescaled1 = rescaled1 - np.min(rescaled1)
	rescaled1 = rescaled1 / np.max(rescaled1)
	rescaled1 =  cv2.resize(rescaled1, (img.shape[1],img.shape[0]))

	rescaled2  =np.flip(output2[0,:,:,0],axis=1)
	rescaled2 = rescaled2 - np.min(rescaled2)
	rescaled2 = rescaled2 / np.max(rescaled2)
	rescaled2 =  cv2.resize(rescaled2, (img.shape[1],img.shape[0]))
	rescaled=(rescaled1+rescaled2)/2
	return rescaled
def q_depth(img):
	input1 = np.clip(np.asarray(img, dtype=float) / 255, 0, 1)
	output1 = predict(model, input1)
	rescaled1 =output1[0,:,:,0]
	rescaled1 = rescaled1 - np.min(rescaled1)
	rescaled1 = rescaled1 / np.max(rescaled1)
	rescaled1 =  cv2.resize(rescaled1, (img.shape[1],img.shape[0]))
	return rescaled1

while 1:
	t = time.time()
	ret, img =cap.read()
	img = cv2.resize(img, (64*4,48*4))
	op=depth(img)
	#cv2.imshow("res",op)
	#cv2.imshow("input",img)
	mask = cv2.inRange(op*255,0, 50)
	print(time.time()-t , "sec")
	obj =cv2.bitwise_and(img,img, mask=mask)
	back = img
	back = cv2.GaussianBlur(back,(5,5),0)
	back = cv2.GaussianBlur(back,(5,5),0)
	back = cv2.GaussianBlur(back,(5,5),0)
	back = cv2.bitwise_and(back,back, mask=255-mask) 
	potrait = back + obj
	#cv2.imshow("obj",obj)
	cv2.imshow("potrait ",potrait)
	cv2.imshow("depth",op)
	key = cv2.waitKey(1)
	if key == 27:
		break
    
cap.release()
cv2.destroyAllWindows()	