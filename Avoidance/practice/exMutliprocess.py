from multiprocessing import Process, Queue, Pipe
from time import sleep
import time
import numpy as np

def while0(send_img, send_yaw, recv_rc, recv_ack): # Drone
    n = 0
    list_ =[]
    while True:
        img = np.random.randint(0,255,size=(192,256,3))
        if recv_ack.poll():
            print(recv_ack.recv())
            send_img.send(img)
            print("sent img", img)
        print("maden list", img)
        send_yaw.send(n%181)
        a, b, c, d = recv_rc.recv()
        print(time.time(), "rc", a, b, c, d)
        n += 1
        sleep(1)
    send_img.close()
    send_yaw.close()

def while1(send_state, send_ack, recv_img): # comDepth
    while True:
        wake = False
        #img = recv_img.recv()
        img = recv_img.recv() if recv_img.poll() else None
        print("img",img)
        sleep(3)

        #bool =True if(len(img)%10==0) else False
        bool=True
        send_state.send(bool)
        wake = True
        send_ack.send(wake)
        wake = False

    send_state.close()
    send_ack.close()

def while2(send_rc, recv_yaw, recv_state): # compVelo
    while True:
        y = recv_yaw.recv()
        print(time.time(), "yaw",y)
        state = recv_state.recv() if recv_state.poll() else None
        print("state", state)
        rc = 0, 0, 0, 0
        if state == True:
            rc = 5, 5, 5, 5+y
        send_rc.send(rc)
        sleep(1)
    send_rc.close()


if __name__ == '__main__':
    send_img, recv_img = Pipe() # proc0 -> proc1
    send_ack, recv_ack = Pipe() # proc1 -> proc0
    send_state, recv_state = Pipe() # proc1 -> proc2
    send_yaw, recv_yaw = Pipe() # proc0 -> proc2
    send_rc, recv_rc = Pipe() # proc2 -> proc2
    process1 = Process(target=while0, args=(send_img, send_yaw, recv_rc, recv_ack, ))
    process2 = Process(target=while1, args=(send_state, send_ack, recv_img, ))
    process3 = Process(target=while2, args=(send_rc, recv_yaw, recv_state, ))
    process1.start()
    process2.start()
    process3.start()
    #print(sender.recv())
    process1.join()
    process2.join()
    process3.join()
