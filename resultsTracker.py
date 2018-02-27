import matplotlib.pyplot as plt
import numpy as np

DEBUG = False
def plotRegret(rawResults,labels,optMean):

    plt.figure(1)

    for algIndex,top_list in enumerate(rawResults):
        #each one of these corresponds to results for one algorithm
        avg_list = None
        for i,trial in enumerate(top_list):
            if (DEBUG):
                print "Trial (",i,") Algorithm (",a,") = ",trial
            #each on of these are the results of one trial
            if (avg_list == None):
                #add reward from trial to avg list 
                avg_list = np.array([e[1] for e in trial])
            else:
                #add reward from trial to avg list 
                avg_list = avg_list + np.array([e[1] for e in trial])

        avg_list = [(a/float(len(top_list))) for a in avg_list]

        cum_reward = np.cumsum(avg_list)
        opt_reward = [optMean*i for i in range(len(cum_reward))]
        plt.plot(range(len(cum_reward)),opt_reward - cum_reward,label=labels[algIndex])

    plt.legend()
    plt.show()


