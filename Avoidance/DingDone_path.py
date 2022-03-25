from djitellopy import tello
from exDepth import * # with first version
from Avoidance import * # with second version
import time
import cv2


def compVelo(obs, target, yaw, r_l, f_b, u_d, y):
    #target = 0 if dir=="up" else 180
    detect = False
    print("target", target, "current_yaw", yaw, "yaw_velocity", y)
    # detect: object: object가 한가운데 없는 경우 -> object가 가운데에 있을때까지 object 방향으로 조금씩 회전하면서 직진: return 0,speed,0,y
    if detect:
        print("detect")
    # avoid : 장애물이 있는 경우 -> 장애물 안보일때까지 장애물 반대방향으로 회전하면서 직진: return 0,speed,0,y
    elif obs[1][1] == True:
        print("avoidance")
        r_l, f_b, u_d, y = doAvoid(obs, r_l, f_b, u_d, y)
    # forward: yaw=0혹은 yaw=180인 경우 -> 그냥 직진: return 0,speed,0,0
    elif abs(abs(yaw) - target) < 5:
        print("forward")
        pass
    # return: yaw!=0 혹은 yaw!=180인 경우 -> yaw=0 혹은 yaw=180이 될때까지 회전하면서 직진: return 0,speed,0,-yaw 혹은 -abs(180-yaw)
    else:
        print("return")
        r_l, f_b, u_d, y = re_turn(yaw, target, r_l, f_b, u_d, y)
    print("target", target, "current_yaw", yaw, "yaw_velocity", y)

    return r_l, f_b, u_d, y

me = tello.Tello()
me.connect()
print(me.get_battery())
me.streamon()

grid = 5 #(cm)
row = 4 #(grid) # larger than 1
col = 1 #(grid) # larger than 1
x, y = 0, 0
c = 0
r = 0
speed = 5
lat = 5
start, end = 0, 0

me.takeoff()
me.send_rc_control(0, 0, 0, 0)

rl, fc, ud, y = 0, speed, 0, 0

for c in range(col):
    target = 0 if col%2==0 else 180
    for r in range(row):
        if ((c == 0) or (c == col-1)) and (r == row-1): target = (target+180) % 360
        elif (c>0 and c<(col-1)) and (r == row-2): target = (target+180) % 360
        grid_num = int(grid/(lat))
        print("grid_num", grid_num)
        for g in range(grid_num):
            start = time.time()
            # img 받음
            img = me.get_frame_read().frame
            img = cv2.resize(img, (64*4,48*4))
            cv2.imshow("streaming", img)
            cv2.waitKey(1)

            # depth 계산
            depth_, time3 = depth(me, img, start)
            # 영상 이미지를 3x3의 영역으로 나누어 depth계산
            area, time4 = mk_area(me, depth_*255, time3)
            obs = detObstacle(area, 30)
            print(me.get_battery())
            # 주행 방향 결정
            print("get yaw", me.get_yaw())
            rl, fc, ud, y = compVelo(obs, target, me.get_yaw(), rl, fc, 0, y)
            print("yaw velocity", y)
            # 해당 방향으로 주행
            me.send_rc_control(rl, fc, ud, y)
            # img 출력
            time5 = time.time()
            print("gap", time5 - time4)
            img = me.get_frame_read().frame
            img = cv2.resize(img, (64*4,48*4))
            cv2.imshow("streaming", img)
            cv2.waitKey(1)
            end = time.time()
            print("latency", end-start)
            real_lat = end-start
            time.sleep(max(0, lat-real_lat))

me.send_rc_control(0, 0, 0, 0)
me.land()
