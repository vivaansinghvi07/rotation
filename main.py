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
    
    def dist(self, x, y, z):
        return math.sqrt((x-self.x)**2 
                       + (y-self.y)**2 
                       + (z-self.z)**2)
    
def blue_after(prompt):
    """ Makes the string end in a blue colored prompt, and begin with a color reset. """
    return Color.RESET_COLOR + prompt + Color.BLUE

def rectangular_prism_points(l, w, h, n, point):

    # determine if needs to automatically calc center
    if point == "-1":
        x0, y0, z0 = -l/2, -w/2, -h/2
    else:
        x0, y0, z0 = map(lambda x: -x, map(float, point.split(',')))

    points_per_unit = (n / (l*w*h)) ** (1/3)

    points = [Point(x, y, z) for x in np.linspace(x0, x0+l, round(l*points_per_unit))
                             for y in np.linspace(y0, y0+w, round(w*points_per_unit))
                             for z in np.linspace(z0, z0+h, round(h*points_per_unit))]
    
    lim = max(map(lambda i: abs(i)/2, [l, w, h])) + max(map(abs, [x0, y0, z0]))

    return points, lim
    
def sphere_points(r, n, point):

    # determine if needs to automatically calc center
    if point == "-1":
        x0, y0, z0 = 0, 0, 0
    else:
        x0, y0, z0 = map(lambda x: -x, map(float, point.split(',')))

    points_per_unit = (n/(4/3*np.pi*r**3))**(1/3)*2 # fit to cube
    
    points = [point for x in np.linspace(x0-r, x0+r, round(r*points_per_unit))
                    for y in np.linspace(y0-r, y0+r, round(r*points_per_unit))
                    for z in np.linspace(z0-r, z0+r, round(r*points_per_unit))
                    if (point:=Point(x, y, z)).dist(x0, y0, z0) <= r]

    lim = max(map(abs, [x0, y0, z0])) + 2 * r

    return points, lim

def tetrahedron_points(s, n, point):

    # ratio for calculating height
    h = math.sqrt(3)/2

    # determine if needs to automatically calc center
    if point == "-1":
        x0, y0, z0 = 0, 0, (s*h*2/3)
    else:
        x0, y0, z0 = map(lambda x: -x, map(float, point.split(',')))

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

def rotating_gif(frames, fps, points, pitch, roll, yaw):

    ax = plt.axes(projection="3d")
    os.mkdir("imgs")

    i = 1
    points, lim = points 
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

    # creates images array and depth counter
    images, i = [], 1

    # adds images to the images array
    while True:
        try:
            images.append(imageio.imread(f"imgs/{i}.png"))
            i += 1
        except:
            break

    try: name = sys.argv[1]
    except: name = "plot.gif"

    # saves the gif
    imageio.mimsave(name, images, fps=fps)

    # deletes all the images
    for i in range(1, len(images)+1):
        os.remove(f"imgs/{i}.png")
    os.rmdir("imgs")

def main():

    # get the input
    duration = float(input("Enter the duration of the rotation in seconds (or -1 for auto): "))
    fps = int(input(blue_after("Enter the frames per second: ")))
    assert 0 < fps <= 60, Color.RESET_COLOR + "FPS must be at least 1 or at most 60."
    pitch, roll, yaw = [float(input(blue_after(f"Enter the target {var} in degrees: ")))
                        for var in ["pitch", "roll", "yaw"]]
    
    rect = "Rectangular Prism"
    sphere = "Sphere"
    tetra = "Tetrahedron"

    shape = pynterface.numbered_menu([rect, sphere, tetra], beginning_prompt=Color.RESET_COLOR + "Select the type of shape to be modeled: ")
    
    if shape == sphere:
        r = float(input(blue_after("Enter the radius of the sphere: ")))
        n = int(input(blue_after("Enter an approximate number of points: ")))  
        point = input(blue_after("Enter the point to revolve around in the format \"x, y, z\", or -1 to revolve around the center: "))
        points = sphere_points(r, n, point)
    elif shape == rect:
        l, w, h = map(float, input(blue_after("Enter the dimensions seperated by commas in the form \"l, w, h\": ")).split(','))   
        n = int(input(blue_after("Enter an approximate number of points: ")))
        point = input(blue_after("Enter the point to revolve around in the format \"x, y, z\", or -1 to revolve around the center: "))
        points = rectangular_prism_points(l, w, h, n, point)
    elif shape == tetra:
        s = float(input(blue_after("Enter a side length: ")))
        n = int(input(blue_after("Enter an approximate number of points: ")))
        point = input(blue_after("Enter the point to revolve around in the format \"x, y, z\", or -1 to revolve around the center: "))
        points = tetrahedron_points(s, n, point)
    
    # calculate number of frames given fps and speed
    if duration == "-1":
        frames = max([pitch, roll, yaw]) / 5
    else:
        frames = duration * fps

    print(end=Color.RESET_COLOR)
    method = pynterface.numbered_menu(["gif", "other"], beginning_prompt="Enter the type of output:")
    if method == "gif":
        rotating_gif(int(frames), fps, points, pitch, roll, yaw)
    elif method == "other":
        print("Other methods not supported yet!")

if __name__ == "__main__":
    rotating_gif(
        frames=100,
        fps=30,
        points=tetrahedron_points(
            s=5,
            n=100,
            point="-1"
        ),
        pitch=360,
        roll=0,
        yaw=0
    )