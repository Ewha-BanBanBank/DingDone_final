import numpy as np

def detObstacle(depth_, crit):
    obs = depth_ <= crit
    return obs
'''
def doAvoid(obs, r_l, f_b, u_d, y):
    yaw = 20
    if obs[1, 2]:
        y = -yaw
        print("turn left")
    else:
        y = yaw
        print("turn right")
    
    if np.logical_and((sum(obs[:2, :2]) >= 4), (sum(obs[:2, 2]) <= 1)).any(): 
        # Code of "(sum(obs[:2, :2]) >= 4) and (sum(obs[:2, 2]) <= 1):" makes ValueError: The truth value of an array with more than one element is ambiguous. Use a.any() or a.all()
        #if obs[1,2] == True: u_d = 5
        y = yaw
        print("turn right")
    elif np.logical_and((sum(obs[:2, 1:]) >= 4), (sum(obs[:2, 0]) <= 1)).any():
        #if obs[1,0] == True: u_d = 5
        y = -yaw
        print("turn left")
    elif sum(obs[1]) == 3:
        print("turn right")
        u_d = yaw
    elif np.logical_and((sum(obs[:2,0]) == 2), (sum(obs[:2, 1:]) <= 2)).any():
        y  = yaw
        print("turn right")
    elif np.logical_and((sum(obs[:2,2]) == 2), (sum(obs[:2, :2]) <= 2)).any():
        y  = -yaw
        print("turn left")
    elif sum(obs[:2, 0]) == 0:
        y = yaw
        print("turn right")
    elif sum(obs[:2, 2]) == 0:
        y = -yaw
        print("turn left")
    elif sum(obs[:2, :]) == 1:
        y = yaw
        print("turn right")
    else: y = yaw
    
    return r_l, f_b, u_d, y
'''

def re_turn(yaw, target, f_b):
    '''
    if target == 0:
        if
        y = -(yaw - target) # -(yaw - target)/2
    elif target == 180:
        y = yaw - target # (yaw - target)/2
    '''
    y = target - yaw
    if abs(y) >= 90:
        y = int(y/2)
    elif abs(y) >= 45:
        y = int(y/3)
    else:
        y = int(y)
    print("turn", y)
    return f_b, y



