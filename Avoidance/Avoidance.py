from time import sleep
import numpy as np


class Avoidance:
    def __init__(self, tello, depth, prevCase, angle, turn, speed=10):
        # depth은 narray from np
        self.me = tello
        self.depth = depth
        self.prevCase = prevCase
        self.turn = turn
        self.crit = 90 # critical of deciding to close distance
        self.obs = self.depth <= self.crit
        self.speed = speed
        
        # decide type of avoidance
        self.obsType()

        # compute angle to turn and the number of remained turn
        #self.computeAngle(angle)

        
        #self.avoid()
    
    def obsType(self):
        idx = []
        for i in range(len(self.obs)): idx.append(False not in self.obs)
        if False in self.obs: # have no obstacle in video
            self.isAvoid = False
            self.Case = 0

        elif True in idx: # when row that filled with obstance captured from video area exists more than one
            self.isAvoid = True
            self.Case = 1
        
        else: # when obstacle is captured from video area
            self.isAvoid = True
            self.Case = 2
        return self.isAvoid

    def computeAngle(self, angle):
        if self.Case == 1:
            if (self.prevCase != self.Case) or (self.turn == 0):
                self.angle = 80 # one of [60, 70, 80, 90]
                self.turn = 1

        elif self.Case == 2:
            if (self.turn == 0) or (self.prevCase != self.Case):
                s_angle = 45
                self.angle = 90 if np.sum(self.obs) > 4 else s_angle # rotate diffent angle as size of obstacle 
                self.turn = 2

        else:
            self.angle = angle
            self.turn -= 1

    def avoid(self, ): # doing avoidance on case type
        if self.Case == 1:
            if self.turn == 1: # rotate counter clockwise
                self.me.send_fc_control(0, self.speed*2, 0, -(self.angle+10))

            elif self.turn == 0: # rotate clockwise
                self.me.send_fc_control(0, self.speed*2, 0, (self.angle+10)*2)

        elif self.Case == 2:
            if self.turn == 2:
                self.me.send_fc_control(0, self.speed*2, 0, -(self.angle+10))

            elif self.turn == 1:
                self.me.send_fc_control(0, self.speed*2, 0, self.angle+10)
                self.me.rotate_clockwise(2*self.angle)
            
            else: 
                self.me.rotate_counter_clockwise(self.angle)
        sleep(2)
        return self.Case, self.angle, self.turn
