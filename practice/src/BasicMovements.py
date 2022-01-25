from djitellopy import tello
from time import sleep # command에 delay 추가하기 위함

me = tello.Tello()
me.connect()
print(me.get_battery())


me.takeoff()
# me.move_forward(30)

# forward 방향으로 30만큼의 속도로 sleep한 초만큼 이동
me.send_rc_control(0, 30, 0, 0) # yaw_velocity : rotation velocity
sleep(1) # 단위: sec

me.send_rc_control(0, 0, 0, 0) # 착륙시키기 전에 멈추게
me.land()
