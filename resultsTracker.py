import matplotlib.pyplot as plt
import numpy as np
from masterTestbed import BanditSimulator

DEBUG = False

def plotRegret(rawResults,decisionRegionTracker,paramText,labels,optMean,optIndex,armMeans):

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
    plt.figtext(0.99,0.01,"armmeans = " + str(armMeans) + "\n"+paramText,horizontalalignment = 'right')
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


    
    plt.legend()
    plt.figtext(0.99,0.01,"armmeans = " + str(armMeans) +"\n"+ paramText,horizontalalignment = 'right')
    
    """
    Show decision region weight evolution
    """
    for algIndex,top_list in enumerate(decisionRegionTracker):
        if (labels[algIndex] == "MA-TS"):
            plt.figure(3+algIndex)
            #create a list of numArms length
            numArms= len(armMeans)
            tracker = []
            for _ in range(numArms):
                tracker.append([])
            #zip together all trials together
            for i,trial in enumerate(top_list):
                #each on of these are the results of one trial
                for j in range(numArms):
                    #horizon-length tracker list hasnt been created
                    if (i == 0):
                        #take jth element of list and make a horizon-length list of weights
                        tracker[j] = np.array([e[j] for e in trial])
                    else:
                        tracker[j] = tracker[j] + np.array([e[j] for e in trial])
            #plot each arm decision region weight over time
            for j in range(numArms):
                curLabel = "arm " + str(j) + " [{0:.3f}".format(float(armMeans[j])) + "]"
                plt.plot(range(len(tracker[j])),tracker[j],label=curLabel)

            plt.title("Decision Region Post. Dist Mass")
            plt.figtext(0.99,0.01,"armmeans = " + str(armMeans) +"\n"+ paramText,horizontalalignment = 'right')
            plt.legend()


    """
    Show all plots
    """
    plt.show()



def plotClusterPosteriors(listOfBanditSims):
    print "Plotting cluster posteriors"
    for bSim in listOfBanditSims:
        #Get a 
        decisionRegionTracker = b.decisionRegionTracker

def plotTeamBoxes(banditSimulation):
    print "Plotting team boxes"
