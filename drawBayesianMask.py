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
        0.8,          # width
        0.5,          # height
        color="green",
        alpha=0.3
    )
l1x = 0.1
l1y = 0.1
h1x = 0.9
h1y = 0.6

p2 = Rectangle(
        (0.25, -0.1),   # (x,y)
        0.75,          # width
        1.2,          # height
    )

l2x = 0.25
l2y = -0.1
h2x = 0.5
h2y = 1.1



ax.add_patch(p1)
art3d.pathpatch_2d_to_3d(p1, z=0, zdir="z")

#ax.add_patch(p2)
#art3d.pathpatch_2d_to_3d(p2, z=-0.25, zdir="z")



X = np.arange(0, 1, 0.05)
Y = np.arange(0, 1, 0.05)
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
        if (w2 < 0):
            Z2[i][j] = 0.0
            continue
        else:
            #if y coordinate inside the boy
            if (w2 <= h2y - l2y):
                successProb = successProb * float(w2/(h2y-l2y))
            

        Z2[i][j] = successProb



X, Y = np.meshgrid(X, Y)


# Plot the surface.
surf1 = ax.plot_surface(X, Y, Z1, cmap=cm.coolwarm,
                       alpha=0.7,linewidth=0, antialiased=False)

#surf2 = ax.plot_surface(X, Y, Z2, cmap=cm.plasma,
#                       linewidth=0, antialiased=False)

# Customize the z axis.
ax.set_zlim(.00, 1.00)
ax.zaxis.set_major_locator(LinearLocator(10))
ax.zaxis.set_major_formatter(FormatStrFormatter('%.02f'))

# Add a color bar which maps values to colors.
fig.colorbar(surf1, shrink=0.5, aspect=5)
#fig.colorbar(surf2, shrink=0.5, aspect=5)

plt.show()
