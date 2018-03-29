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

fig = plt.figure()
ax = fig.gca(projection='3d')

# Ma.ke data.
p1 = Rectangle(
        (0.1, 0.1),   # (x,y)
        1,          # width
        1,          # height
    )
l1x = 0.1
l1y = 0.1
h1x = 1.1
h1y = 1.1

p2 = Rectangle(
        (0.15, 0.05),   # (x,y)
        1,          # width
        0,          # height
    )

l2x = 0.15
l2y = 0.05
h2x = 1.15
h2y = 1.05



ax.add_patch(p1)
art3d.pathpatch_2d_to_3d(p1, z=-0.5, zdir="z")

ax.add_patch(p2)
art3d.pathpatch_2d_to_3d(p2, z=-0.25, zdir="z")



X = np.arange(-1, 1, 0.1)
Y = np.arange(-1, 1, 0.1)
Z1 = np.zeros((len(X),len(Y)))
for (i,x) in enumerate(X):
    for (j,y) in enumerate(Y):
        successProb = 1.0

        w = h1x - x
        print "W is",w
        if (w <= 0.0):
            Z1[i][j] = 0.0
            continue
        else:
            #if x coordinate inside the box
            if (w <= h1x - l1x):
                successProb = successProb * float(w/(h1x-l1x))
         
        w = h1y - y
        if (w < 0):
            Z1[i][j] = 0.0
            continue
        else:
            #if y coordinate inside the boy
            if (w <= h1y - l1y):
                successProb = successProb * float(w/(h1y-l1y))
            

        Z1[i][j] = successProb

X, Y = np.meshgrid(X, Y)


# Plot the surface.
surf = ax.plot_surface(X, Y, Z1, cmap=cm.coolwarm,
                       linewidth=0, antialiased=False)

#surf = ax.plot_surface(X, Y, Z2, cmap=cm.coolwarm,
#                       linewidth=0, antialiased=False)

# Customize the z axis.
ax.set_zlim(-1.01, 1.01)
ax.zaxis.set_major_locator(LinearLocator(10))
ax.zaxis.set_major_formatter(FormatStrFormatter('%.02f'))

# Add a color bar which maps values to colors.
fig.colorbar(surf, shrink=0.5, aspect=5)

plt.show()
