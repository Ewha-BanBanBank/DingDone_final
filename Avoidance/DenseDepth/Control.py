## contol drone and estimate position of drone simply
from Avoidance_v0 import *
from time import sleep
import numpy as np


class Control:
    def __init__(self, tello, depth, grid, height, width, y, x, speed=10):
        self.me = tello
        self.depth = depth
        self.grid = grid
        self.row = int(height/grid)
        self.col = int(width/grid)
        self.y, self.x  = y, x # cm
        self.direction = "up"
        self.speed = speed
        self.yaw = 45 
        self.degree = 30 # degree of 30
        self.dir[2] = ["up", "down"]
        self.n = 0
        
    def PathPlan(self, ):
        rot = int(180/self.degree) # 180 / degree_rotate_one_sec
        self.n = 0
        self.direction = self.dir[self.n]
        self.case = 0
        self.angle = 0
        self.turn = 0
        for i in range(self.col):
            # move up(foward) or down(backward) as high as height
            for j in range(self.row): 
                for g in range(self.grid):
                    # move up(foward) or down(backward) as high as grid
                    avoid = Avoidance(self.me, self.depth, self.case, self.angle, self.turn)
                    if avoid:
                        avoid.computeAngle()
                        self.case, self.angle, self.turn = avoid.avoid()
                        g-=1
                    else:
                        self.forward(self.direction)
            for r in range(rot): # rorate degree of 180(=30*6)
                if ((rot%2 == 1) and (r == (int(rot/2)))):
                    self.me.send_fc_control(0, self.speed, 0, self.yaw)
                    sleep(1)
                    self.x += (self.degree/self.speed) / rot
                else:
                    self.rotate(self.direction, rot)
                    if (r == (int(rot/2)-1)):
                        self.direction = self.dir[self.n]
                        n = (n+1)%2

    def forward(self, direction):
        self.me.send_fc_control(0, self.speed, 0, 0)
        sleep(1)
        if direction == "up":
            self.y += self.speed
        elif direction == "down":
            self.y -= self.speed
        
    def rotate(self, direction,  rot):
        self.me.send_fc_control(0, self.speed, 0, self.yaw)
        sleep(1)
        r = self.degree/self.speed
        if direction == "up":
            self.y += r/rot # approximation value
        else:
            self.y -= r/rot
        self.x += r/rot # r*sin(yaw)

    def get_point(self, ):
        return self.y, self.x
