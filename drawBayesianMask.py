'''
======================
3D surface (color map)
======================

Demonstrates plotting a 3D surface colored with the coolwarm color map.
The surface is made opaque by using antialiased=False.

Also demonstrates using the LinearLocator and custom formatting for the
z axis tick labels.
'''
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, PathPatch,Rectangle
# register Axes3D class with matplotlib by importing Axes3D
from mpl_toolkits.mplot3d import Axes3D
import mpl_toolkits.mplot3d.art3d as art3d
from matplotlib.text import TextPath
from matplotlib.transforms import Affine2D

from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter
import numpy as np
import math

PLOT_ALL,PLOT_MAX = (True,False)

np.random.seed(1771)
colors = ['b','r','g',"purple","orange",'y']
fig = plt.figure()
ax = fig.gca(projection='3d')

"""
 #Specific to 2 rectangles

# Ma.ke data.
p1 = Rectangle(
        (0.3, -0.3),   # (x,y)
        0.4,          # width
        0.4,          # height
        color="green",
        alpha=0.3
    )
l1y = 0.3
l1x = -0.3
h1y = 0.7
h1x = 0.1

p2 = Rectangle(
        (-0.5, 0.5),   # (x,y)
        0.2,          # width
        0.4,          # height
        color="purple",
        alpha=0.3
    )

l2y = -0.5
l2x = 0.5
h2y = -0.3
h2x = 0.9



ax.add_patch(p1)
art3d.pathpatch_2d_to_3d(p1, z=0, zdir="z")

ax.add_patch(p2)
art3d.pathpatch_2d_to_3d(p2, z=0, zdir="z")



X = np.arange(-1, 1, 0.01)
Y = np.arange(-1, 1, 0.01)
Z1 = np.zeros((len(X),len(Y)))
Z2 = np.zeros((len(X),len(Y)))
for (i,x) in enumerate(X):
    for (j,y) in enumerate(Y):
        successProb = 1.0

        w1 = h1x - x
        if (w1 <= 0.0):
            Z1[i][j] = 0.0
            continue
        else:
            #if x coordinate inside the box
            if (w1 <= h1x - l1x):
                successProb = successProb * float(w1/(h1x-l1x))
        w1 = h1y - y
        if (w1 < 0):
            Z1[i][j] = 0.0
            continue
        else:
            #if y coordinate inside the boy
            if (w1 <= h1y - l1y):
                successProb = successProb * float(w1/(h1y-l1y))

        Z1[i][j] = successProb

        #2nd
        successProb = 1.0
        w2 = h2x - x
        if (w2 <= 0.0):
            Z2[i][j] = 0.0
            continue
        else:
            #if x coordinate inside the box
            if (w2 <= h2x - l2x):
                successProb = successProb * float(w2/(h2x-l2x))
        w2 = h2y - y
        if (w2 <= 0):
            Z2[i][j] = 0.0
            continue
        else:
            #if y coordinate inside the boy
            if (w2 <= h2y - l2y):
                successProb = successProb * float(w2/(h2y-l2y))

        Z2[i][j] = successProb

print "Prob mask",Z1

X, Y = np.meshgrid(X, Y)


# Plot the surface.
#surf1 = ax.plot_surface(X, Y, Z1, cmap=cm.coolwarm,
#                       alpha=0.75,linewidth=0, antialiased=True)

surf2 = ax.plot_surface(X, Y, Z2, cmap=cm.coolwarm,
                       linewidth=0, alpha=0.75, antialiased=False)

"""

# Arbitrary number of rectangles

# Make data.
NUM_RECTS = 2
TEAMSIZE = 3
RES = 0.1
#very likely bounds
x_globmin,x_globmax,y_globmin,y_globmax = (10000,-10000,10000,-10000)
rects = []

for i in range(NUM_RECTS):
    x_coord = np.random.normal((1,TEAMSIZE))/3.0
    x_min,x_max = (np.min(x_coord),np.max(x_coord))

    y_coord = np.random.normal((1,TEAMSIZE))/3.0
    y_min,y_max = (np.min(y_coord),np.max(y_coord))

    print "Coorindates for team ",i, " are", x_coord,y_coord
    print "Boundaries are x in ",x_min,",",x_max,"; y in ",y_min,",",y_max


    if (x_globmin > x_min):
       x_globmin = x_min

    if (x_globmax < x_max):
        x_globmax = x_max


    if (y_globmin > y_min):
        y_globmin = y_min


    if (y_globmax < y_max):
        y_globmax = y_max


    rect = Rectangle(
        (x_min,y_min),   # (x,y)
        x_max-x_min,          # width
        y_max-y_min,          # height
        color=colors[i],
        alpha=0.3
    )
    ax.add_patch(rect)
    art3d.pathpatch_2d_to_3d(rect, z=(-0.5 + i/10.0), zdir="z")
    rects.append((x_globmin,x_globmax,y_globmin,y_globmax))

print "Boundaries are x in ",x_globmin,",",x_globmax,"; y in ",y_globmin,",",y_globmax

X = np.arange(math.floor(x_globmin),math.ceil(x_globmax),RES)
Y = np.arange(math.floor(y_globmin),math.ceil(y_globmax),RES)
print "X = ",X
print "Y = ",Y
Z = {}

for i in range(NUM_RECTS+1):
    Z[i] = []
print Z

for (k,rect) in enumerate(rects):
    print "Team k's rect is:",rect
    for (i,x) in enumerate(X):
        for (j,y) in enumerate(Y):

            xmin,xmax,ymin,ymax = rect
            prob = 1.0

            # x;s
            fx = xmax - x
            if (fx <= 0.0):
               prob = 0.0

            elif (fx < xmax - xmin):
                prob = prob * float(fx/(xmax-xmin))
            #y;s
            fy = ymax - y

            if (fy <= 0.0):
               prob = 0.0

            elif (fx < xmax - xmin):
                prob = prob * float(fx/(xmax-xmin))

            print "Success probability of team ",k," on pt ", (x,y),"is ",prob
            Z[k].append(prob)

X, Y = np.meshgrid(X, Y)
print "All Z:",Z

# Plot the surface.
#surf1 = ax.plot_surface(X, Y, Z1, cmap=cm.coolwarm,
#                       alpha=0.75,linewidth=0, antialiased=True)
"""
PLot all
"""
if (PLOT_ALL):
    surf = None

    for i in range(NUM_RECTS):
        surf = ax.plot_surface(X, Y, np.array(Z[i]).reshape((len(X),len(Y))), cmap=cm.coolwarm, linewidth=0, alpha=0.75, antialiased=False)

    # Customize the z axis.
    ax.set_zlim(-1, 1.00)
    ax.zaxis.set_major_locator(LinearLocator(10))
    ax.zaxis.set_major_formatter(FormatStrFormatter('%.02f'))

    ax.set_xlabel("Task X Coordinate")
    ax.set_ylabel("Task Y Coordinate")
    ax.set_zlabel("Team Success Probability")

    # Add a color bar which maps values to colors.
    #fig.colorbar(surf1, shrink=0.5, aspect=5)
    fig.colorbar(surf, shrink=0.5, aspect=5)

if (PLOT_MAX):
    fig2 = plt.figure()
    ax = fig2.gca(projection='3d')
    surf = ax.plot_surface(X, Y, Z[-1], cmap=cm.coolwarm, linewidth=0, alpha=0.85, antialiased=False)
    # Customize the z axis.
    ax.set_zlim(.00, 1.00)
    ax.zaxis.set_major_locator(LinearLocator(10))
    ax.zaxis.set_major_formatter(FormatStrFormatter('%.02f'))

    ax.set_xlabel("Task X Coordinate")
    ax.set_ylabel("Task Y Coordinate")
    ax.set_zlabel("Team Success Probability")

    # Add a color bar which maps values to colors.
    #fig.colorbar(surf1, shrink=0.5, aspect=5)
    fig2.colorbar(surf, shrink=0.5, aspect=5)


plt.show()
