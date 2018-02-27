import matplotlib.pyplot as plt
import numpy as np

def plotRegret(rawResults,labels):

    plt.figure(1)

    for top_list in rawResults:
        #each one of these corresponds to results for one algorithm
        avg_list = None
        for trial in top_list:
            #each on of these are the results of one trial
            if (avg_list == None):
                #add reward from trial to avg list 
                avg_list = [e[1] for e in trial]
            else:
                #add reward from trial to avg list 
                avg_list = avg_list + [e[1] for e in trial]

        avg_list = [(a/float(len(top_list))) for a in avg_list]

        cum_regret = np.cumsum(avg_list)
        plt.plot(range(len(cum_regret)),cum_regret)

    plt.show()


