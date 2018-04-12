'''
=========================
3D surface (checkerboard)
=========================

Demonstrates plotting a 3D surface colored in a checkerboard pattern.
'''

from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.ticker import LinearLocator
from armModel import getSuccessProb as rectSuccessProb

import numpy as np

num_rects = 8
rects = []
fig = plt.figure()
ax = fig.gca(projection='3d')

# Make data.
X = np.arange(-5, 5, 0.2)
xlen = len(X)
Y = np.arange(-5, 5, 0.2)
ylen = len(Y)
assert(len(X)==len(Y))

X, Y = np.meshgrid(X, Y)
Z = np.array(-1*X**2 + -1*Y**2)


#source of randomness
np.random.seed(17761)
r = np.random.normal(0,1,(1000*num_rects))
Zdict = {}

for i,n in enumerate(range(num_rects)):
    xs = r[(n*4*i):(n*4*i + 2)]
    ys = r[(n*4*i+2):(n*4*i + 4)]
    print i,xs,ys
    rect = (np.min(xs),np.max(xs),np.min(ys),np.max(ys))
    print rect
    rects.append(rect)
    print "Added rectangle (xmin,xmax,ymin,ymax)",rect
    Zdict[i] = np.array(Z,copy=True)
    #now: Zdict and rects tied to same set of keys (ints 0,...)

# Create an empty array of strings with the same shape as the meshgrid, and
# populate it with two colors in a checkerboard pattern.
colortuple = ('b', 'g', 'r', 'c', 'm', 'y', 'k', 'w')
colors = np.empty(X.shape, dtype=str)
for y in range(ylen):
    for x in range(xlen):
        colors[x, y] = colortuple[(x + y) % len(colortuple)]

Zmax = np.copy(Zdict[0])

for key in Zdict.keys():
    zs = np.array([rectSuccessProb((x,y),rects[key]) for x,y in zip(np.ravel(X),np.ravel(Y))])
    Zs = zs.reshape(X.shape)
    surf = ax.plot_surface(X, Y, Zs, facecolor=colortuple[key], linewidth=0,alpha=0.6)
    #update max
    print "OLD Zmax",Zmax
    Zmax = np.maximum(Zdict[key],Zmax)
    print "New ZMax",Zmax



        
# Plot the surface with face colors taken from the array we made.


# Customize the z axis.
ax.set_zlim(0, 1)
ax.set_zlabel("Success Probability")
ax.set_ylabel("Latent Dimension 1")
ax.set_xlabel("Latent Dimension 2")

ax.w_zaxis.set_major_locator(LinearLocator(6))



fig = plt.figure()
ax = fig.gca(projection='3d')
ax.plot_wireframe(X,Y,Zmax)

plt.show()
