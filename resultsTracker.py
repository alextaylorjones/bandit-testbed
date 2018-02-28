import matplotlib.pyplot as plt
import numpy as np

DEBUG = False
def plotRegret(armMeans,rawResults,paramText,labels,optMean,optIndex):

    plt.figure(1)

    for algIndex,top_list in enumerate(rawResults):
        #each one of these corresponds to results for one algorithm
        """
        Plot Regret
        """
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

    plt.title("Empirical Expected Regret")
    plt.figtext(0.99,0.01,paramText,horizontalalignment = 'right')
    plt.legend()


    plt.figure(2)
    plt.title("Arm Selection Counts (assuming unique optimal)")
    for algIndex,top_list in enumerate(rawResults):

        """
        Plot Number of times optimal arm has been selected
        """
        
        optCountList = None 
        for i,trial in enumerate(top_list):
            if (optCountList == None):
                optCountList = []
                for index,reward in trial:
                    if (index == optIndex):
                        optCountList.append(1)
                    else:
                        optCountList.append(0)
            else:
                for i,(index,reward) in enumerate(trial):
                    if (index == optIndex):
                        optCountList[i] = optCountList[i] + 1 

        optCountListCum = np.cumsum(np.array(optCountList))

        plt.plot(range(len(optCountListCum)),optCountListCum,label=labels[algIndex])


    
    """
    Show all plots
    """
    plt.legend()
    plt.figtext(0.99,0.01,paramText,horizontalalignment = 'right')
    #plt.show()


