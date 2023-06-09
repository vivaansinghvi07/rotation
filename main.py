from __future__ import annotations
import matplotlib.pyplot as plt
import numpy as np
from math import sin, cos, radians as rad
import imageio
import os
import sys
import pynterface
import math
from pynterface import Color
from typing import Literal

class Point:
    def __init__(self, x, y, z) -> None:
        self.x = x
        self.y = y
        self.z = z

    def __str__(self) -> str:
        return f"({self.x}, {self.y}, {self.z})"
    
    def __repr__(self) -> str:
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
    
    def dist(self, x, y, z) -> float:
        return math.sqrt((x-self.x)**2 
                       + (y-self.y)**2 
                       + (z-self.z)**2)
    
def blue_after(prompt: str) -> str:
    """ Makes the string end in a blue colored prompt, and begin with a color reset. """
    return Color.RESET_COLOR + prompt + Color.BLUE

def rectangular_prism(l: float, w: float, h: float, n: int, point: tuple | Literal[-1]) -> tuple[list[Point], float]:

    """
    The point [0, 0, 0] is assumed to be the lowest point in value of the rectangular prism.
    Meaning that, assuming [l, w, h] are all non-negative, it will have the lowest [x, y, z] values.
    """

    # determine if needs to automatically calc center
    if point == -1:
        x0, y0, z0 = -l/2, -w/2, -h/2
    else:
        x0, y0, z0 = map(lambda x: -x, point)

    points_per_unit = (n / (l*w*h)) ** (1/3)

    points = [Point(x, y, z) for x in np.linspace(x0, x0+l, round(l*points_per_unit))
                             for y in np.linspace(y0, y0+w, round(w*points_per_unit))
                             for z in np.linspace(z0, z0+h, round(h*points_per_unit))]
    
    lim = max(map(lambda i: abs(i)/2, [l, w, h])) + max(map(abs, [x0, y0, z0]))

    return (points, lim)
    
def sphere(r: float, n: int, point: tuple | Literal[-1]) -> tuple[list[Point], float]:
    
    """
    The point [0, 0, 0] is assumed to be the center.
    The program assigning different values to the center is merely to simulate rotation around a point.
    """

    # determine if needs to automatically calc center
    if point == -1:
        x0, y0, z0 = 0, 0, 0
    else:
        x0, y0, z0 = map(lambda x: -x, point)

    points_per_unit = (n/(4/3*np.pi*r**3))**(1/3)*2 # fit to cube
    
    points = [point for x in np.linspace(x0-r, x0+r, round(r*points_per_unit))
                    for y in np.linspace(y0-r, y0+r, round(r*points_per_unit))
                    for z in np.linspace(z0-r, z0+r, round(r*points_per_unit))
                    if (point:=Point(x, y, z)).dist(x0, y0, z0) <= r]

    lim = max(map(abs, [x0, y0, z0])) + 2 * r

    return points, lim

def tetrahedron(s: float, n: int, point: tuple | Literal[-1]) -> tuple[list[Point], float]:

    """
    [0, 0, 0] is assumed to be the tip of the triangle.
    """

    # ratio for calculating height
    h = math.sqrt(3)/2

    # determine if needs to automatically calc center
    if point == -1:
        x0, y0, z0 = 0, 0, (s*h*2/3)
    else:
        x0, y0, z0 = map(lambda x: -x, point)

    points_per_side = round((n*(math.sqrt(72)))**(1/3))

    def gen_triangle(x0, y0, z0, it, pps, slen):

        # determine the coordinates of the other points
        points = []
        pz = z0 - it / pps * slen * h   # height level
        for i in range(it): # "it" determines how many levels there are in the triangle
            py = y0 + - (i - ((it-1) * 2/3)) * slen / pps * h # for each row
            for j in range(i+1):
                px = x0 + (j - i / 2) * (slen / pps)
                points.append(Point(px, py, pz))
        
        return points
    
    points = []
    for i in range(points_per_side):
        # generate a base traingle centered around x0, y0, z0
        temp_points = gen_triangle(x0, y0, z0, i, points_per_side, s)   
        points.extend(temp_points)      # extend the temp points array

    lim = max(map(abs, [x0, y0, z0-(s*h*2/3)])) + s * 0.5
    
    return points, lim

def rotating_gif(frames: int, fps: int, shape: tuple[list[Point], float], name: str, 
                 pitch: float | int, roll: float | int, yaw: float | int) -> None:

    ax = plt.axes(projection="3d")
    try: os.mkdir("imgs")
    except: pass

    i = 1
    points, lim = shape 
    pitch, roll, yaw = map(rad, [pitch, roll, yaw])

    
    for p, r, y in zip(np.linspace(0, pitch, frames), 
                       np.linspace(0, roll, frames), 
                       np.linspace(0, yaw, frames)):

        # rotate points
        rotated = [point.rotated(p, r, y) for point in points]    

        # fetch values
        x_vals = [point.x for point in rotated]
        y_vals = [point.y for point in rotated]
        z_vals = [point.z for point in rotated]

        ax.set_aspect('auto')

        # plot settings
        ax.scatter3D(x_vals, y_vals, z_vals)
        ax.set_xlim(-lim, lim)
        ax.set_ylim(-lim, lim)
        ax.set_zlim(-lim, lim)
        plt.grid(False)
        plt.axis('off')
        plt.savefig(f"imgs/{i}.png", bbox_inches='tight')
        plt.cla()

        # increment plot name counter
        i += 1

    plt.close()

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
    imageio.mimsave(name, images, fps=fps)

    # deletes all the images
    for i in range(1, len(images)+1):
        os.remove(f"imgs/{i}.png")
    os.rmdir("imgs")

def main():

    # get the input
    duration = float(input(blue_after("Enter the duration of the rotation in seconds (or -1 for auto): ")))
    fps = int(input(blue_after("Enter the frames per second: ")))
    assert 0 < fps <= 60, Color.RESET_COLOR + "FPS must be at least 1 or at most 60."
    pitch, roll, yaw = [float(input(blue_after(f"Enter the target {var} in degrees: ")))
                        for var in ["pitch", "roll", "yaw"]]
    
    rect = "Rectangular Prism"
    sph = "Sphere"
    tetra = "Tetrahedron"

    shape = pynterface.numbered_menu([rect, sph, tetra], beginning_prompt=Color.RESET_COLOR + "Select the type of shape to be modeled: ")
    
    n = int(input(blue_after("Enter an approximate number of points: ")))  
    point = input(blue_after("Enter the point to revolve around in the format \"x, y, z\", or -1 to revolve around the center: "))
    if point == '-1': point = -1
    else: point = tuple(map(float, point.split(',')))

    # obtain the points for the thing
    if shape == sph:
        r = float(input(blue_after("Enter the radius of the sphere: ")))
        shape = sphere(r, n, point)
    elif shape == rect:
        l, w, h = map(float, input(blue_after("Enter the dimensions seperated by commas in the form \"l, w, h\": ")).split(','))   
        shape = rectangular_prism(l, w, h, n, point)
    elif shape == tetra:
        s = float(input(blue_after("Enter a side length: ")))
        shape = tetrahedron(s, n, point)
    else:
        print("Invalid shape!")
        exit()
    
    # calculate number of frames given fps and speed
    if duration == -1:
        frames = max([pitch, roll, yaw]) / 5
    else:
        frames = duration * fps

    try: name = sys.argv[1]
    except: name = "plot.gif"

    print(end=Color.RESET_COLOR)
    method = pynterface.numbered_menu(["gif", "other"], beginning_prompt="Enter the type of output:")
    if method == "gif":
        rotating_gif(
            frames=int(frames),
            fps=fps,
            shape=shape,
            name=name,
            pitch=pitch,
            roll=roll,
            yaw=yaw
        )
    elif method == "other":
        print("Other methods not supported yet!")

def demo():

    """ Used to create the examples. """

    try: os.mkdir('demo')
    except: pass
    os.chdir('demo')

    rotating_gif(
        frames=600,
        fps=60,
        shape=rectangular_prism(
            l=4, w=5, h=9,
            n=200,
            point=(4, 5, 2)
        ),
        name="rect.gif",
        pitch=702,
        roll=-349.2,
        yaw=204
    )

    rotating_gif(
        frames=300,
        fps=60,
        shape=sphere(
            r=5,
            n=200,
            point=(1, 1, 1)
        ),
        name="sphere.gif",
        pitch=360,
        roll=360,
        yaw=-360
    )

    rotating_gif(
        frames=360,
        fps=60,
        shape=tetrahedron(
            s=4,
            n=50,
            point=-1
        ),
        name="tetrahedron.gif",
        pitch=0,
        roll=360,
        yaw=0
    )

if __name__ == "__main__":
    main()
