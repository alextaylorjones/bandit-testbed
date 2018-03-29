import matplotlib.pyplot as plt
import numpy as np
from masterTestbed import BanditSimulator
import math

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

    """
    Show all plots
    """
    plt.show()


#clusterSizes = a list of part sizes (assumes arms are ordered)
def plotClusterPosteriors(listOfBanditSims,listOfClusterSizes):
    print "Plotting cluster posteriors"
    
    plt.figure(5)
    
    for index,b in enumerate(listOfBanditSims):
        clusterSizes = listOfClusterSizes[index]

        #Ensure this bandit sim had clustered arm scheme 
        if (len(b.paramDict["arm scheme"]) > 2):
            if (b.paramDict["arm scheme"][1].startswith("clustered") == False):
                continue

        decisionRegionTracker = b.decisionRegionTracker
        for algIndex,top_list in enumerate(decisionRegionTracker):
            if (b.paramDict["algorithms"][algIndex].endswith("TS") == False):
                #only plot TS results
                continue
                
            #create a list of length= number of clusters
            numClusters = len(clusterSizes)
            tracker = []
            for _ in range(len(clusterSizes)):
                tracker.append([])
            #zip together all trials together
            for i,trial in enumerate(top_list):
                #each on of these are the results of one trial
                clusterId = 0
                clusterCount = 0
                for j in range(b.paramDict["num arms"]):
                    #ensure we are appending to the right cluster tracker
                    clusterCount = clusterCount + 1
                    if (clusterCount > clusterSizes[clusterId]):
                        clusterId = clusterId + 1
                        clusterCount = 1

                    #horizon-length tracker list hasnt been created
                    if (i == 0):
                        #take jth element of list and make a horizon-length list of weights
                        print "Trial Results",trial
                        tracker[clusterId] = np.array([e[j] for e in trial])
                    else:
                        print "Trial Results",trial
                        tracker[clusterId] = tracker[clusterId] + np.array([e[j] for e in trial])
            for i in range(len(clusterSizes)):
                #normalize tracker over the number of trials
                tracker[i] = tracker[i] * (1.0/len(top_list))
                #label with current algorithm and cluster ID
                curLabel = "cluster " + str(j) + "" + b.paramDict["algorithms"][algIndex]
                #plot
                plt.plot(range(len(tracker[i])),tracker[i],label=curLabel)

        plt.title("Decision Region Post. Dist Mass")
        plt.figtext(0.99,0.01,"armmeans = " + str(bSim.armMeans) +"\n"+ paramText,horizontalalignment = 'right')
        plt.legend()

    plt.show()

def plotTeamBoxes(banditSimulation):
    print "Plotting team boxes"
