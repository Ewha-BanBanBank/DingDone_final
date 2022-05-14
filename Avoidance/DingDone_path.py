from exDepth import * # import depth estimation function  # with second version
from Avoidance import * # import function changing drone's speed  # with second version
import time
from time import sleep
import cv2
from multiprocessing import Process, Pipe

def Drone(send_img, send_yaw, recv_rc, recv_ack): # control drone and streaming video

    ###########################################################
    # initialize drone
    sleep(6)
    fly = True
    me = tello.Tello()
    me.connect()
    print(me.get_battery())
    me.streamon()

    grid = 5  # (cm)
    row = 25  # (*0.5 grid) # larger than 1
    col = 1  # (grid) # larger than 1
    x, y = 0, 0
    c = 0
    r = 0
    speed = grid # 1초에 grid(cm)만큼씩 이동
    lat = 1 #latency of depth estimation
    start, end = 0, 0
    if fly:
        me.takeoff()
        me.send_rc_control(0, 0, 0, 0)

    rl, fc, ud, y = 0, speed, 0, 0
    ###########################################################
    # control drone
    # speed = 5 <=> 1초에 5cm 이동
    c = 0
    target = 0
    first_ack = True
    print("start yaw", me.get_yaw())
    while True:
        if c >= col : break
        print("#################################column", c,"#################################")
        # target = 0 if c % 2 == 0 else 180
        r = 0 #if ((c == 0) or (c == col - 1)) else 1
        curve = False
        while True:
            if r >= (row) : break
            if curve == False and r == row-1 and c < col-1:
                curve = True
                target = (target + 180) % 360
            start = time.time()
            #print("end~start", start-end)
            ##################################
            img = me.get_frame_read().frame
            img = cv2.resize(img, (64 * 4*2, 48 * 4*2)) ## initial size = (64*4, 48*4)
            send_yaw_list = [speed, target, me.get_yaw()]
            #print("I sent yaw list", send_yaw_list)
            send_yaw.send(send_yaw_list)
            #print("I will receive rc")
            avoid = False
            if recv_rc.poll(): speed, y, avoid , sleep_ = recv_rc.recv()
            #print("I received",speed, y)
            #print("do process1 poll?")
            cv2.imshow("streaming", img)

            cv2.waitKey(1)
            if recv_ack.poll() :# or first_ack:
                #first_ack = False
                ack = recv_ack.recv()
                if ack:
                    #print("I received ack")
                    #print("I will send image")
                    send_img.send(img)
                    #print("I sent image")
            #print("target", target, "current_yaw", send_yaw_list[2], "yaw_velocity", y)
            end = time.time()
            if avoid == False: me.send_rc_control(0, speed, 0, y)
            else: me.send_rc_control(0, speed * int(12/sleep_), 0, y);#sleep(sleep_)
            # 장애물과의 거리가 가까울수록 sleep_ 작은값

            ##################################
            real_lat = end-start
            #print("real_lat", real_lat)
            sleep(max(0, lat-real_lat))
            if lat>1: lat=0.5
            if curve and y != 0: r -= 1
            r += 1
        #if c == 0: speed += 3
        c += 1
    ###########################################################
    if fly:
        me.send_rc_control(0, 0, 0, 0)
        me.land()
    send_img.send("Done")
    send_yaw.send("Done")
    send_img.close()
    send_yaw.close()

def compDepth(send_avoid, send_ack, recv_img):
    crit_obs = 70
    est = estDepth()

    while True:
        # receive image from process0
        ack = True
        #print("I will send ack", ack)
        send_ack.send(ack)
        #print("I sent ack")
        ack = False
        print("I will receive image if proc0 sent it")
        #print("poll?",recv_img.poll())
        img = recv_img.recv()
        #print("I receive image")
        #if recv_img.poll():
        #    print("recv_image poll")
        #    img = recv_img.recv()
        #else: img = 100

        avoid = "forward"
        # img shpae is (192, 256, 3)
        if(type(img) == type("str")): break
        #print("I receive image")

        # compute depth
        #print("compute depth")
        start = time.time()
        depth_= est.depth(img)
        #cv2.imshow("depth", depth_)  # (window name, mat)
        print(time.time() - start)
        # 영상 이미지를 3x3의 영역으로 나누어 depth계산
        #print("compute area")
        area = est.mk_area(depth_*255)
        #print("compute obs")
        obs = detObstacle(area, crit_obs)
        sleep_ = 3
        if obs[1,0] or obs[1,1] or obs[1,2] : #obs[1][1] == True:
            if obs[1, 2] or obs[1, 1]:# > obs[1,2]:
                if area[1, 2] < 30: sleep_ = 3
                avoid = "left"
            else:
                if area[1, 0] < 30 or area[1, 1] < 30: sleep_ = 3
                avoid = "right"
        #print("I will send avoid state")
        if avoid != "forward": avoid_list = avoid, sleep_
        else: avoid_list = None
        send_avoid.send(avoid_list)
    print("comDepth is dead")
    send_ack.close()
    send_avoid.close()


def compVelo(send_rc, recv_yaw, recv_avoid):
    sleep(5)
    while True:
        #target = 0 if dir=="up" else 180
        detect = False
        avd = False
        turn = 35
        recv_yaw_list = recv_yaw.recv()
        if type(recv_yaw_list) == type("str"):break
        speed, target, yaw = recv_yaw_list
        #print("I will receive avoid state")
        avoid_list = recv_avoid.recv() if recv_avoid.poll() else None
        avoid = None
        sleep_ = None
        if avoid_list != None: avoid, sleep_ = avoid_list

        #print("avoid ",avoid,"sleep",sleep_)
        y = 0
        # detect: object: object가 한가운데 없는 경우 -> object가 가운데에 있을때까지 object 방향으로 조금씩 회전하면서 직진: return 0,speed,0,y
        if detect:
            print("--detect--")
        # avoid : 장애물이 있는 경우 -> 장애물 안보일때까지 장애물 반대방향으로 회전하면서 직진: return 0,speed,0,y
        elif avoid == "right":
            avd = True
            print("!!avoidance!! - turn right")
            y = turn
        # forward: yaw=0혹은 yaw=180인 경우 -> 그냥 직진: return 0,speed,0,0
        elif avoid == "left":
            avd = True
            print("!!avoidance!!- turn left")
            y = -turn
        elif (abs(abs(yaw) - target) < 3) or (target == 180 and yaw<-177):
            print("~~forward~~")
            pass
        # return: yaw!=0 혹은 yaw!=180인 경우 -> yaw=0 혹은 yaw=180이 될때까지 회전하면서 직진: return 0,speed,0,-yaw 혹은 -abs(180-yaw)
        else:
            print("**return**")
            speed, y = re_turn(yaw, target, speed)

        send_rc_list = speed, y, avd, sleep_
        send_rc.send(send_rc_list)

    send_rc.close()
    print("closed precess2")


if __name__ == '__main__':
    '''
    model_path = 'nyu.h5'
    # Custom object needed for inference and training
    custom_objects = {'BilinearUpSampling2D': BilinearUpSampling2D, 'depth_loss_function': None}
    model_depth = load_model(model_path, custom_objects=custom_objects, compile=False)
    print("depth model loading completed")
    # model.summary()
    '''
    send_img, recv_img = Pipe() # proc0 -> proc1
    send_ack, recv_ack = Pipe() # proc1 -> proc0
    send_avoid, recv_avoid = Pipe() # proc1 -> proc2
    send_yaw, recv_yaw = Pipe() # proc0 -> proc2
    send_rc, recv_rc = Pipe() # proc2 -> proc2

    proc0 = Process(target=Drone, args=(send_img, send_yaw, recv_rc, recv_ack, ))
    proc1 = Process(target=compDepth, args=(send_avoid, send_ack, recv_img,))
    proc2 = Process(target=compVelo, args=(send_rc, recv_yaw, recv_avoid,))
    proc0.start()
    proc1.start()
    proc2.start()
    proc0.join()
    proc1.join()
    proc2.join()
