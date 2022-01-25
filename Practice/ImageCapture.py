import cv2
from djitellopy import tello

me = tello.Tello()
me.connect()
print(me.get_battery())

me.streamon()

while True:
    img = me.get_frame_read().frame
    img = cv2.resize(img, (360, 240))
    cv2.imshow("Image", img) #(window name, mat)
    cv2.waitKey(1) # sleep과 같은 동작

