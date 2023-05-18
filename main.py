from __future__ import annotations
import matplotlib.pyplot as plt
import numpy as np
from math import sin, cos
import imageio.v2 as imageio
import os

class Point:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __str__(self):
        return f"({self.x}, {self.y}, {self.z})"
    
    def __repr__(self):
        return str(self)
    
    def rotated(self, yaw, pitch, roll) -> Point:
        x, y, z = self.x, self.y, self.z
        a, b, c = yaw, pitch, roll
        sa, sb, sc = sin(a), sin(b), sin(c)
        ca, cb, cc = cos(a), cos(b), cos(c)
        newx = (x*ca*cb + y*(ca*sb*sc-sa*cc) + z*(ca*sb*cc+sa*sc))
        newy = (x*sa*cb + y*(sa*sb*sc+ca*cc) + z*(sa*sb*cc-ca*sc))
        newz = (x*-sb   + y*cb*sc            + z*cb*cc) 
        return Point(newx, newy, newz)
    
def make_gif():

    # creates images array and depth counter
    images, i = [], 1

    # adds images to the images array
    while True:
        try:
            images.append(imageio.imread(f"imgs/{i}.png"))
            i += 1
        except:
            break

    # saves the gif
    imageio.mimsave("plot.gif", images, duration=0.05, loop=0)

    # deletes all the images
    for i in range(1, len(images)+1):
        os.remove(f"imgs/{i}.png")

ax = plt.axes(projection="3d")
points = [Point(x, y, z) for x in range(-5, 6) for y in range(-5, 6) for z in range(0, 10)]

for i, pitch in enumerate(np.linspace(0, np.pi, 40), start=1):

    rotated = [p.rotated(pitch, 0, 0) for p in points]    

    x_vals = [p.x for p in rotated]
    y_vals = [p.y for p in rotated]
    z_vals = [p.z for p in rotated]

    ax.scatter3D(x_vals, y_vals, z_vals)
    ax.set_xlim(-7, 7)
    ax.set_ylim(-7, 7)
    ax.set_zlim(0, 10)
    plt.savefig(f"imgs/{i}.png")
    plt.cla()

make_gif()