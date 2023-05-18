from __future__ import annotations
import matplotlib.pyplot as plt
import numpy as np
from math import sin, cos, radians as rad
import imageio
import os
import pynterface
from pynterface import Color

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
    
def make_gif(fps):

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
    imageio.mimsave("plot.gif", images, fps=fps)

    # deletes all the images
    for i in range(1, len(images)+1):
        os.remove(f"imgs/{i}.png")

def rotating_gif(frames, fps, pitch, roll, yaw):

    ax = plt.axes(projection="3d")
    points = [Point(x, y, z) for x in range(-5, 6) for y in range(-5, 6) for z in range(-5, 6)]

    i = 1

    for p, r, y in zip(np.linspace(0, pitch, frames), 
                       np.linspace(0, roll, frames), 
                       np.linspace(0, yaw, frames)):

        rotated = [point.rotated(p, r, y) for point in points]    

        x_vals = [point.x for point in rotated]
        y_vals = [point.y for point in rotated]
        z_vals = [point.z for point in rotated]

        ax.scatter3D(x_vals, y_vals, z_vals)
        ax.set_xlim(-7, 7)
        ax.set_ylim(-7, 7)
        ax.set_zlim(-7, 7)
        plt.grid(False)
        plt.axis('off')
        plt.savefig(f"imgs/{i}.png")
        plt.cla()

        i += 1

    make_gif(fps)

def main():

    # get the input
    frames = int(input("Enter the number of frames (-1 for auto): " + Color.BLUE))
    fps = int(input(Color.RESET_COLOR + "Enter the frames per second: " + Color.BLUE))
    pitch, roll, yaw = [float(input(Color.RESET_COLOR + f"Enter the target {var} in degrees: " + Color.BLUE))
                        for var in ["pitch", "roll", "yaw"]]
    
    # automatically determine number of frames (currently 60 per full rotation)
    if frames == -1:
        frames = int(max([pitch, roll, yaw]) // 6)

    print(end=Color.RESET_COLOR)
    method = pynterface.numbered_menu(["gif", "other"], beginning_prompt="Enter the type fo output:")
    if method == "gif":
        rotating_gif(frames, fps, *map(rad, [pitch, roll, yaw]))


if __name__ == "__main__":

    main()