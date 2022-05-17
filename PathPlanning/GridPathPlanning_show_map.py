import math
import time
from djitellopy import tello
import cv2
import numpy as np
from time import sleep
import threading

# import KeyPressModule as kp

width = 200
height = 40
grid = 20
n = 0
x = 500
y = 500

# center = (0, 0)
points = [(500, 500)]
direction = 0

def stay():
    me.send_rc_control(0, 0, 0, 0)

def drawPoints(img, points, return_):
    prev = points[0]
    for point in points[1:]:
        cv2.line(img, (int(prev[0]), int(prev[1])), (int(point[0]), int(point[1])), (0, 0, 255), 5)
        prev = point
    cv2.circle(img, (int(points[-1][0]), int(points[-1][1])), 7, (0, 255, 0), cv2.FILLED)
    cv2.putText(img, f'({(points[-1][0] - 500) / 100:.2f}, {(-1) * (points[-1][1] - 500) / 100:.2f})m',
                (int(points[-1][0]) + 10, int(points[-1][1]) + 30),  # text 위치
                cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 255), 1)
    #cv2.putText(img, f'{me.get_flight_time():.0f}', (800, 100), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1)
    cv2.putText(img, f'flight time: {time.time():.0f}', (800, 120), cv2.FONT_HERSHEY_PLAIN, 1, (255, 255, 255), 1)
    if return_:
        cv2.putText(img, f'Return Mode', (800, 150), cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 0), 1)


def showMap(return_=False):
    img = np.zeros((1000, 1000, 3), np.uint8)
    drawPoints(img, points, return_)
    cv2.imshow("Map", img)
    cv2.waitKey(1)


'''
gridPathPlanning
드론의 현재 위치에 따라 드론의 진행 방향을 맞게 조절하여 모든 grid 영역을 주행할 수 있는 함수

드론의 각 위치 point값을 저장해놓을 list 필요 - 그래야 드론의 이동 경로를 시각화할 수 있음 -> points = [(0, 0), (0, 0)]

input : 
    w: 드론이 주행하려는 총 영역의 넓이
    h: 드론이 주행하려는 총 영역의 높이
    grid: 드론 주행 영역의 한 grid의 변 길이
    point: 드론의 현 위치 (x, y)
    direction: 드론이 주행하려는 방향 (왼쪽으로는 주행하지 않는다)
        0 : up (and rotate clockwise 90)
        1: down (and rotate clockwise -90)
        2: right (and rotate clockwise 90)
        3: right (and rotate clockwise -90)
    speed: 드론 주행 속도

output: 
    주행 후 드론의 위치(x, y)
    드론의 다음 direction


main 
direction 초기값 0
'''


# 0->5가 아니라 0->1->2->3->4->5로 points에 넣어서 경로가 조금씩 같은 간격으로 그려지게끔 구현하기
# 1초에 한번씩 forward, backward, right함수 call해서 1초에 얼마씩 이동하도록
def forward(point, grid, f_time):  # def forward(me, point, grid, speed):
    x, y = point[0], point[1]
    sleep(f_time)
    y -= grid
    return x, y


def backward(point, grid, f_time):  # def backward(me, point, grid, speed):
    x, y = point[0], point[1]
    sleep(f_time)
    y += grid
    return x, y


def right(point, grid, f_time):  # def right(me, point, grid, speed):
    x, y = point[0], point[1]
    sleep(f_time)
    x += grid
    return x, y


def left(point, grid, f_time):
    x, y = point[0], point[1]
    sleep(f_time+1)
    x -= grid
    return x, y


def back(point, grid, f_time, angle):
    x, y = point[0], point[1]
    sleep(f_time+1)
    x -= grid * np.sin(angle)
    y += grid * np.cos(angle)
    return x, y



def rotate_clock(me):
    me.rotate_clockwise(90)
    stay()
    sleep(2)

def rotate_counterclock(me):
    me.rotate_counter_clockwise(90)
    stay()
    sleep(2)


def gridPathPlanning(w, h, grid, points, direction, notLast=True, speed=10):
    row = h // grid
    point = points[-1]
    global x, y  # global 선언 유무 비교
    f_time = 2

    if direction == 0:  # up
        me.send_rc_control(0, speed, 0, 0)
        for i in range(row):
            point = forward(point, grid, f_time)  # forward(me, point, grid, speed)
            points.append(point)

            print("x,y", point[0], point[1], "forward")
            showMap()
        if(notLast): rotate_clock(me);direction = 2

    elif direction == 1:  # down
        me.send_rc_control(0, speed, 0, 0)
        for i in range(row):
            point = backward(point, grid, f_time)  # backward(me, point, grid, speed)
            points.append(point)
            print("x,y", point[0], point[1], "backward")
           showMap()
        if(notLast): rotate_counterclock(me);direction = 3

    elif direction == 2:  # right(with rotate(90))
        me.send_rc_control(0, speed, 0, 0)
        point = right(point, grid, f_time)  # right(me, point, grid, speed)
        points.append(point)
        print("x,y", point[0], point[1], "right")
        showMap()
        if(notLast): rotate_clock(me);direction = 1

    elif direction == 3:  # right(with rotate(-90))
        me.send_rc_control(0, speed, 0, 0)
        point = right(point, grid, f_time)  # right(me, point, grid, speed)
        points.append(point)
        showMap()
        if(notLast): rotate_counterclock(me);direction = 0

    return direction


def Return(point, grid, speed=10):
    x, y = point
    xx = x - 500
    yy = y - 500
    points.append(point)
    print("direction", direction)
    f_time = 2
    if y == 500:
        if direction==0 or direction==1: me.rotate_counter_clockwise(90);print("direction0")
        elif direction==2 or direction==3: me.rotate_clockwise(180);print("direction2")
        me.send_rc_control(0, speed, 0, 0)
        while (point[0] > 500):
            point = left(point, grid, f_time)  # backward(me, point, grid, speed)
            points.append(point)
            print("x,y", point[0], point[1], "return1")
            showMap(True)
    elif x == 500:
        me.rotate_clockwise(180)
        me.send_rc_control(0, speed, 0, 0)
        while (point[1] > 500):
            point = backward(point, grid, f_time)  # backward(me, point, grid, speed)
            points.append(point)
            print("x,y", point[0], point[1], "return2")
            showMap(True)
    else:
        angle = abs(np.arctan(xx / abs(yy)))
        dst = int(abs(yy) / (np.cos(angle)))
        print("angle", math.degrees(angle), int(math.degrees(angle)))
        print("yaw", me.get_yaw())

        if direction==0: me.rotate_counter_clockwise(180-int(math.degrees(angle)));print("direction_0")
        elif direction==1: me.rotate_clockwise(int(math.degrees(angle)));print("direction_1")
        else: me.rotate_clockwise(90+int(math.degrees(angle)));print("direction_2")
        me.send_rc_control(0, speed, 0, 0)

        while (point[0] > 500 or point[1] < 500):
            point = back(point, grid, f_time, angle)  # forward(me, point, grid, speed)
            points.append(point)
            print("x,y", point[0], point[1], "return3")
            showMap(True)
me = tello.Tello()

me.connect()
print(me.get_battery())

me.takeoff()
stay()
sleep(2)
stay()

flight = 3

img_ = np.zeros((1000, 1000, 3), np.uint8)
cv2.imshow("Map", img_)
cv2.waitKey(1)
'''
p1 = threading.Thread(target=Receive)
p2 = threading.Thread(target=Display)
p1.start()
p2.start()
'''
while (n < flight):
    notLast = True
    img = np.zeros((1000, 1000, 3), np.uint8)
    if(n>=(1+2*int(width/grid))):break
    if(n==flight-1): notLast = False

    if (n == 0):
        cv2.imshow("Map", img)
        cv2.waitKey(1)


    direction = gridPathPlanning(width, height, grid, points, direction, notLast)

    n += 1
Return(points[-1], grid)
stay()
me.land()
sleep(10)
