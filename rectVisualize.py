import math
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
def visualizeRects(givenRects=None,givenTaskLocation=None,posterior=None,iterationCount=None,trialCount = None,chosenTeam=None):
    #constants

    CLUSTER_RANDOM = False
    CLUSTER_EXAMPLE = 0 #set >0 for specific example
    NUM_RECTS = 2
    EPSILON = 0.333
    XMIN,YMIN = (-1,-1)
    XMAX,YMAX = (1,1)
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
    xPts = np.arange(XMIN, XMAX, 0.02)
    xlen = len(xPts)
    yPts = np.arange(YMIN, YMAX, 0.02)
    ylen = len(yPts)

    assert(len(xPts)==len(yPts))
    X, Y = np.meshgrid(xPts, yPts)
    Z = np.array(-1*X**2 + -1*Y**2)


    #source of randomness
    #CLustered Random:
    #16392 w/ 3x3 - smooth
    #183822 w 4x2 - almost discrete
    #822 w/ 4x2
    np.random.seed(8220)
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


    ## Choose "nice" task location if none is given

    taskLocation = None
    taskLocationIdx = None
    if (givenTaskLocation is None):
        c = 0 
        while (taskLocation == None and c < 1000):
            xStarIdx = np.random.randint(0,int(xlen))
            xStar = xPts[xStarIdx]
            yStarIdx = np.random.randint(0,int(ylen))
            yStar = yPts[yStarIdx]
            print "Checking potential ",(xStar,yStar)
             
            for i in range(num_rects):
                print i
                sProb = rectSuccessProb((xStar,yStar),rects[i])
                if (sProb > 0.1 and sProb < 0.9):
                    taskLocation = (xStar,yStar)
                    taskLocationIdx = (xStarIdx,yStarIdx)
                    break
            c = c + 1

    else:
        taskLocation = givenTaskLocation

    print "Selected task location ",taskLocation

    # Create an empty array of strings with the same shape as the meshgrid, and
    # populate it with two colors in a checkerboard pattern.
    colortuple = ('b', 'g', 'r', 'c', 'm', 'y', 'k', 'w')
    colors = np.empty(X.shape, dtype=str)
    for y in range(ylen):
        for x in range(xlen):
            colors[x, y] = colortuple[(x + y) % len(colortuple)]

    Zmax = np.copy(Zdict[0])

    """
    Plot probability surface
    """ 

    skip = False

    if (iterationCount != None and trialCount != None):
        if (iterationCount > 0 or trialCount > 0):
            skip = True

    if (skip == False):

        fig = plt.figure(figsize=plt.figaspect(1.0/num_rects))
        for i,rect in enumerate(rects):

            print "Rect", i, " = ",rect
            zs = np.array([rectSuccessProb((x,y),rects[i]) for x,y in zip(np.ravel(X),np.ravel(Y))])

            Zs = zs.reshape(X.shape)

            ax = fig.add_subplot(1,num_rects,i+1,projection='3d')
            ax.plot_surface(X,Y,Zs,linewidth=0.1,color=colortuple[i])

            ax.set_title("Probability of Success over Task Points for Team %i" % (i))
            ax.set_zlabel("Success Probability",fontsize=DEFAULT_FONT_SZ)
            ax.set_xlabel("Latent Dimension 1",fontsize=DEFAULT_FONT_SZ)
            ax.set_ylabel("Latent Dimension 2",fontsize=DEFAULT_FONT_SZ)
            
            ax.view_init(60,35)

            plt.savefig('./posterior/prob-surfaces')
                

    """ 
    Plot divergence surface for each rect

    """
    
    skip = False

    if (iterationCount != None and trialCount != None):
        if (iterationCount > 0 or trialCount > 0):
            skip = True

    if (skip == False):
        fig = plt.figure(figsize=plt.figaspect(1.0/num_rects))

        for i,rect in enumerate(rects):
           

            zs = np.array([rectSuccessProb((x,y),rects[i]) for x,y in zip(np.ravel(X),np.ravel(Y))])
            Zs = zs.reshape(X.shape)

            successProb = rectSuccessProb(taskLocation,rects[i])
            failProb = 1.0 - successProb
            print "\n\n***Sucess prob for team ", i, " = ",successProb
            divMat = np.empty((xlen,ylen))


            for x in range(xlen):
                for y in range(ylen):
                    #if ((x+y) % 154 == 0):
                    #    print "At point",(xPts[x],yPts[y]),"success of team ",i,"(",rects[i],") is ",Zs[x][y]

                    divMat[x][y] = successProb*math.log(successProb/Zs[x][y]) + failProb*math.log(failProb/(1.0 -Zs[x][y]))

                    
                    if (i == 1 and abs(xPts[x] + 2.0) < 0.05 and abs(yPts[y] + 0.5) < 0.05):
                        print "At point",(xPts[x],yPts[y]),"success probability is",Zs[x][y]," and divergence is",divMat[x][y]

                    #print "GOT HERE for rect",rects[i], "on task ",taskLocation, ". test val idx is ",x,y,"test val is",(xPts[x],yPts[y]),"div is",divMat[x][y]

            print "Div Mat",divMat

            ax = fig.add_subplot(1,num_rects,i+1,projection='3d')
            ax.plot_surface(X,Y,divMat,color=colortuple[i])
            ax.set_title("Divergence for Team %i" % (i))
            ax.set_xlabel("Latent Dimension 1",fontsize=DEFAULT_FONT_SZ)
            ax.set_ylabel("Latent Dimension 2",fontsize=DEFAULT_FONT_SZ)
            plt.tight_layout()
            fig.savefig('./posterior/divergence-surfaces')



    """
    Plot update ratio
 
    fig = plt.figure(figsize=plt.figaspect(2.0/num_rects))

    for i,rect in enumerate(rects):
        zs = np.array([rectSuccessProb((x,y),rects[i]) for x,y in zip(np.ravel(X),np.ravel(Y))])
        Zs = zs.reshape(X.shape,order='F')

        successProb = rectSuccessProb(taskLocation,rects[i])
        failProb = 1.0 - successProb
        print "Sucess prob",successProb
        print "Xlength,",xlen
        ratioMat = np.empty((xlen,ylen))


        for x in range(xlen):
            for y in range(ylen):
                ratioMat[x][y] = Zs[x][y]/successProb


        ax = fig.add_subplot(1,2*num_rects,i*2+1,projection='3d')
        ax.plot_surface(X,Y,ratioMat,color=colortuple[i])
        ax.set_title("Model Ratio Loss (success) for Team %i" % (i))

        for x in range(xlen):
            for y in range(ylen):
                ratioMat[x][y] = (1.0 - Zs[x][y])/failProb

        ax = fig.add_subplot(1,2*num_rects,i*2+2,projection='3d')
        ax.plot_surface(X,Y,ratioMat,color=colortuple[i])
        ax.set_title("Model Ratio Loss (failure) for Team %i" % (i))



    plt.tight_layout()

    """

    """
    Plot posterior
    """
    if (posterior != None and iterationCount != None):
        fig,ax = plt.subplots()
        #ax.plot_surface(X,Y,Zmax,cmap=cm.coolwarm)
        xs = [p[0][0] for p in posterior]
        ys = [p[0][1] for p in posterior]
        ws = [p[1] for p in posterior]

        sc = ax.scatter(xs,ys,cmap='hot',c=ws)
        plt.colorbar(sc)
        ax.set_xlim(XMIN,XMAX)
        ax.set_ylim(YMIN,YMAX)
        ax.set_title("Marginal (t = %i, chosen team =%i) Posterior Probability" % (iterationCount,chosenTeam))
        ax.set_xlabel("Latent Dimension 1",fontsize=DEFAULT_FONT_SZ)
        ax.set_ylabel("Latent Dimension 2",fontsize=DEFAULT_FONT_SZ)
        fig.savefig('./posterior/trial%i-t%i' % (trialCount,iterationCount))


        #plt.title("Success Probability vs Task Location - Maximum over All Teams",fontsize=16)
 
    skip = False

    if (iterationCount != None and trialCount != None):
        if (iterationCount > 0 or trialCount > 0):
            skip = True

    if (skip == False):
        fig,ax = plt.subplots()
        #plt.title("Latent Representation of %i teams in %i clusters" %(num_rects,num_clusters))
        #ax.grid(zorder=0)
        drawRects = []

        for i,rect in enumerate(rects):
            #rect = rects[i]
            rectDraw = mpatches.Rectangle( (rect[0],rect[2]),(rect[1]-rect[0]), (rect[3] - rect[2]),facecolor=colortuple[i],alpha=0.6)
            print "Plotting rects",rectDraw
            ax.add_patch(rectDraw)
            #drawRects.append(rectDraw)

        ax.add_patch(mpatches.Circle(taskLocation,0.02,color='k'))

        #colors = np.random.uniform(0,1,(len(drawRects)))
        #collection = PatchCollection(drawRects, cmap=plt.cm.hsv, alpha=0.6)
        #collection = PatchCollection(drawRects)#, cmap=plt.cm.coolwarm, alpha=0.6)
        #collection.set_array(np.array([0.0,0.3,0.8]))

        #ax.add_collection(collection,)
        ax.set_xlim(XMIN,XMAX)
        ax.set_ylim(YMIN,YMAX)
        ax.set_xlabel("Latent Dimension 1",fontsize=DEFAULT_FONT_SZ)
        ax.set_ylabel("Latent Dimension 2",fontsize=DEFAULT_FONT_SZ)
        plt.savefig('./posterior/latent-team-loc')


    """
    Plot hard suboptimal regions

    """
    skip = False

    if (iterationCount != None and trialCount != None):
        if (iterationCount > 0 or trialCount > 0):
            skip = True

    if (skip == False):
        #Get optimal team
        maxSuccess = 0.0
        optTeam = -1
        for i,rect in enumerate(rects):
            s

        #sanity check
        assert(optTeam >= 0)

        #Find all models in which optimal arm is fixed close to its true distribution
        for i,x in enumerate(xPts):
            for j,y in enumerate(yPts):
                if 
        for i,rect in enumerate(rects):
           

            zs = np.array([rectSuccessProb((x,y),rects[i]) for x,y in zip(np.ravel(X),np.ravel(Y))])
            Zs = zs.reshape(X.shape)

            successProb = rectSuccessProb(taskLocation,rects[i])
            failProb = 1.0 - successProb
            print "\n\n***Sucess prob for team ", i, " = ",successProb
            divMat = np.empty((xlen,ylen))


            for x in range(xlen):
                for y in range(ylen):
                    #if ((x+y) % 154 == 0):
                    #    print "At point",(xPts[x],yPts[y]),"success of team ",i,"(",rects[i],") is ",Zs[x][y]

                    divMat[x][y] = successProb*math.log(successProb/Zs[x][y]) + failProb*math.log(failProb/(1.0 -Zs[x][y]))

                    
                    if (i == 1 and abs(xPts[x] + 2.0) < 0.05 and abs(yPts[y] + 0.5) < 0.05):
                        print "At point",(xPts[x],yPts[y]),"success probability is",Zs[x][y]," and divergence is",divMat[x][y]

                    #print "GOT HERE for rect",rects[i], "on task ",taskLocation, ". test val idx is ",x,y,"test val is",(xPts[x],yPts[y]),"div is",divMat[x][y]

            print "Div Mat",divMat

            ax = fig.add_subplot(1,num_rects,i+1,projection='3d')
            ax.plot_surface(X,Y,divMat,color=colortuple[i])
            ax.set_title("Divergence for Team %i" % (i))
            ax.set_xlabel("Latent Dimension 1",fontsize=DEFAULT_FONT_SZ)
            ax.set_ylabel("Latent Dimension 2",fontsize=DEFAULT_FONT_SZ)
            plt.tight_layout()
            fig.savefig('./posterior/divergence-surfaces')



    
    plt.close()
    #plt.show()

if (__name__ == "__main__"):
    print "Visulizing all team latent boxes"
    visualizeRects()
