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
import matplotlib.patches as mpatches
import numpy as np
from matplotlib.collections import PatchCollection

DEFAULT_FONT_SZ = 16
#input - a list of 4-tuples
def visualizeRects(givenRects=None):
    #constants
    CLUSTER_RANDOM = False
    CLUSTER_EXAMPLE = 1 #set >0 for specific example
    NUM_RECTS = 8
    EPSILON = 0.333
    num_clusters = 1
    
    num_rects = -1
    
    if (givenRects is not None):
        num_rects = len(givenRects)
    else:
        num_rects = NUM_RECTS

    if (givenRects is None and (CLUSTER_RANDOM or CLUSTER_EXAMPLE >0) and num_rects %num_clusters != 0):
        print "Must be even number of arms per cluster in randomly generated instances"
        assert(0)

    rects = []
    fig = plt.figure()
    ax = fig.gca(projection='3d')

    # Make task location pts
    X = np.arange(0, 1, 0.02)
    xlen = len(X)
    Y = np.arange(0, 1, 0.02)
    ylen = len(Y)
    assert(len(X)==len(Y))

    X, Y = np.meshgrid(X, Y)
    Z = np.array(-1*X**2 + -1*Y**2)


    #source of randomness
    #CLustered Random:
    #16392 w/ 3x3 - smooth
    #183822 w 4x2 - almost discrete
    #822 w/ 4x2
    np.random.seed(822)
    r = np.random.uniform(-2.5,1,(1000*num_rects))
    r2 = np.random.uniform(1,1.5,(1000*num_rects))
    #r2 = np.random.uniform(1,1.5,(1000*num_rects))

    Zdict = {}

    if (givenRects is not None):
        rects = givenRects
        print "Rects given, not creating rects"
        for i in range(num_rects):
            Zdict[i] = np.array(Z,copy=True)    

    elif (CLUSTER_RANDOM):
        for i in range(num_clusters):        
                xs = r[(4*i):(4*i + 2)]
                ys = r[(4*i+2):(4*i + 4)]
                print i,xs,ys
                ogRect = (np.min(xs),(np.min(xs) + r2[i*2]),np.min(ys),(np.min(ys)+ r2[i*2+1]))
                for c in range(num_rects/num_clusters):
                    rect = ogRect + np.random.uniform(-EPSILON,EPSILON,(4))
                    
                    rects.append(rect)
                    print "Added rect ",rect
                Zdict[i] = np.array(Z,copy=True)    
    elif (CLUSTER_EXAMPLE > 0):
        for i in range(num_clusters):
            Zdict[i] = np.array(Z,copy=True)
            
        if (CLUSTER_EXAMPLE == 1):
            rects = [ (0.5,0.9,0.1,0.3),(0.1,0.3,0.5,0.9), (0.13,0.27,0.47,0.88)]
    else: #random
        for i,n in enumerate(range(num_rects)):
            xs = r[(4*i):(4*i + 2)]
            ys = r[(4*i+2):(4*i + 4)]
            print i,xs,ys
            rect = (np.min(xs),np.max(xs),np.min(ys),np.max(ys))
            print rect
            rects.append(rect)
            print "Added rectangle (xmin,xmax,ymin,ymax)",rect
            Zdict[i] = np.array(Z,copy=True)  
            #now: Zdict and rects tied to same set of keys (ints 0,...)
    print "Created rects:\n\n",rects
    # Create an empty array of strings with the same shape as the meshgrid, and
    # populate it with two colors in a checkerboard pattern.
    colortuple = ('b', 'g', 'r', 'c', 'm', 'y', 'k', 'w')
    colors = np.empty(X.shape, dtype=str)
    for y in range(ylen):
        for x in range(xlen):
            colors[x, y] = colortuple[(x + y) % len(colortuple)]

    Zmax = np.copy(Zdict[0])

    #for key in Zdict.keys():
    for i,rect in enumerate(rects):

        print "Rect", i, " = ",rect
        zs = np.array([rectSuccessProb((x,y),rects[i]) for x,y in zip(np.ravel(X),np.ravel(Y))])
        Zs = zs.reshape(X.shape)
        surf = ax.plot_surface(X, Y, Zs, facecolor=colortuple[i], linewidth=0,alpha=0.8)
        #update max
        print "OLD Zmax",Zmax
        Zmax = np.maximum(Zs,Zmax)
        print "New ZMax",Zmax



            
    # Plot the surface with face colors taken from the array we made.


    # Customize the z axis.
    ax.set_zlim(0, 1)
    #plt.title("Success Probability vs Task Location - All Teams",fontsize=16)
    ax.set_zlabel("Success Probability",fontsize=DEFAULT_FONT_SZ)
    ax.set_xlabel("Latent Dimension 1",fontsize=DEFAULT_FONT_SZ)
    ax.set_ylabel("Latent Dimension 2",fontsize=DEFAULT_FONT_SZ)

    ax.w_zaxis.set_major_locator(LinearLocator(6))

    fig = plt.figure()
    ax = fig.gca(projection='3d')
    ax.plot_surface(X,Y,Zmax,cmap=cm.coolwarm)
    ax.set_zlabel("Maximum Success Probability",fontsize=DEFAULT_FONT_SZ)
    ax.set_xlabel("Latent Dimension 1",fontsize=DEFAULT_FONT_SZ)
    ax.set_ylabel("Latent Dimension 2",fontsize=DEFAULT_FONT_SZ)
    #plt.title("Success Probability vs Task Location - Maximum over All Teams",fontsize=16)

    fig,ax = plt.subplots()
    #plt.title("Latent Representation of %i teams in %i clusters" %(num_rects,num_clusters))
    #ax.grid(zorder=0)
    drawRects = []

    for i,rect in enumerate(rects):
        #rect = rects[i]
        rectDraw = mpatches.Rectangle( (rect[0],rect[2]),(rect[1]-rect[0]), (rect[3] - rect[2]),facecolor=colortuple[i])
        print "Plotting rects",rectDraw
        drawRects.append(rectDraw)


    #colors = np.random.uniform(0,1,(len(drawRects)))
    #collection = PatchCollection(drawRects, cmap=plt.cm.hsv, alpha=0.6)
    collection = PatchCollection(drawRects, cmap=plt.cm.coolwarm, alpha=0.6)
    #collection.set_array(np.array([0.0,0.3,0.8]))

    ax.add_collection(collection,)
    ax.set_xlim(0,1)
    ax.set_ylim(0,1)
    ax.set_xlabel("Latent Dimension 1",fontsize=DEFAULT_FONT_SZ)
    ax.set_ylabel("Latent Dimension 2",fontsize=DEFAULT_FONT_SZ)
    plt.show()

if (__name__ == "__main__"):
    print "Visulizing all team latent boxes"
    visualizeRects()
