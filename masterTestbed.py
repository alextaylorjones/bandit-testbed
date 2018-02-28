from banditPlayers import BanditPlayer
from armModel import TeamTaskModel, NaiveArmModel
from resultsTracker import plotRegret
import numpy as np
from threading  import Thread

DEBUG = True


class BanditSimulator(Thread):
    paramDict = {}
    results = None
    optAvg = None
    optIndex = None
    armMeans = None

    def __init__(self,paramDict):
        Thread.__init__(self)
        #make a copy
        self.paramDict = dict(paramDict)

    def run(self):
        """Unpack params
        """
        paramDict = self.paramDict
        algorithms = paramDict["algorithms"] 
        armScheme = paramDict["arm scheme"]
        latentDim =   paramDict["latent dimension"] 
        skillDim =  paramDict["skill dimension"] 
        skillDim =  paramDict["num maps"] 
        ttmResolution= paramDict["model task resolution"] 
        ntsResolution =  paramDict["naive param resolution"] 
        trials =  paramDict["trials"] 
        horizon =  paramDict["horizon"] 
        numArms =  paramDict["num arms"] 
        teamSize =  paramDict["team size"] 


        """
        Team Task Model - create once
        contains all potential parameterizations of the team task model
        """
        ttm = TeamTaskModel(latentDim, skillDim, numMaps,ttmResolution, numArms)
        nam = NaiveArmModel(ntsResolution, numArms)

        bp = {}

        #one result list for each algorithm
        results = [[] for _ in algorithms]

        #done once for all trials
        #select team locations, task and mapping 
        teams = []
        if (armScheme[0] == "random"):
            for _ in range(numArms):
                team = np.random.uniform(low=-1.0,high=1.0,size=(teamSize,skillDim))
                teams.append(team)

            #Add skill matrices for teams
            ttm.addTeamSkills(teams)

            #note: currently random choice over all potential models
            ttm.selectTrueModel()

        elif (armScheme[0] == "random-excluded"):
            for _ in range(numArms):
                team = np.random.uniform(low=-1.0,high=1.0,size=(teamSize,skillDim))
                teams.append(team)

            #Add skill matrices for teams
            ttm.addTeamSkills(teams)

            #note: currently random choice over all potential models
            ttm.selectTrueModel(exclude=True)


        else:
            print "No arm scheme by name",
            print armScheme
            assert(False)

     
        for cur_trial in range(trials):
                  
            if (DEBUG):
                print "Starting trial ",cur_trial

            for i in range(len(algorithms)):
                results[i].append([])

            #TODO: generate arm parameters, i.e. team members' skill vectors
            for a in algorithms:
                if (DEBUG):
                    print "(trial ",cur_trial,": time 0) - initialize algorithm ",a

                #model aware thompson sampling
                if (a == "MA-TS"):
                    bp[a] = BanditPlayer(a)
                    bp[a].initMATS(ttm)
                    ttm.reset() # reset param weights
                #naive (model-free) thompson sampling
                elif (a == "naive-TS"):
                    bp[a] = BanditPlayer(a)
                    bp[a].initNaiveTS(nam)
                    nam.reset() #reset param weights
                elif (a == "UCB1"):
                    # do nothing
                    bp[a] = BanditPlayer(a)
                    bp[a].initUCB1(numArms)
                else:
                    print "Algorithm type ", a, " does not exist"

            armSelection = []
            #use the true model to generate random rewards (may or may not be observed)
            rewards,armMeans = ttm.generateAllArmRewards(horizon)

            #Save arm reward means
            if (self.armMeans == None):
                self.armMeans = armMeans
            else: #ensure that these means dont change in between trials
                assert(self.armMeans == armMeans)

            for t in range(horizon):
                print "(trial ",cur_trial,": time ",t,")"

                

                for i,a in enumerate(algorithms):
                    chosenArm = (bp[a]).chooseNextArm(t)
                    if (DEBUG):
                        print "Choosing arm ",chosenArm," for alg ",a

                    (bp[a]).updateModel(chosenArm,rewards[chosenArm][t])
                    
                    """ Calculate the weight of decision region of optimal """
                    #take the results for arm a, taking the latest trial list
                    results[i][-1].append((chosenArm,rewards[chosenArm][t]))

        optAvg = max(ttm.successMeans)
        optIndex = np.argmax(ttm.successMeans)

        #save results in class variables
        self.results = results
        self.optAvg = optAvg
        self.optIndex = optIndex



if __name__ == "__main__":
    print "Running master testbed for bandits"

    #seed
    np.random.seed(70)
    
    armScheme = ("random",None)
    #alg list
    algorithms = ["naive-TS","MA-TS","UCB1"]

    #params for MA-TS
    latentDim = 2
    skillDim = 5
    numMaps = 100
    ttmResolution = 0.1

    #params for naive-TS
    ntsResolution = 0.05

    #general parameters
    trials = 3
    horizon = 300
    numArms = 20
    teamSize = 3

    """
    Fill param dictionary with all params
    """
    paramDict = {}
    paramDict["algorithms"] = algorithms
    paramDict["arm scheme"] = armScheme
    paramDict["latent dimension"] = latentDim
    paramDict["skill dimension"] = skillDim
    paramDict["num maps"] = numMaps
    paramDict["model task resolution"] = ttmResolution
    paramDict["naive param resolution"] = ntsResolution
    paramDict["trials"] = trials
    paramDict["horizon"] = horizon
    paramDict["num arms"] = numArms
    paramDict["team size"] = teamSize

    """
    Run one test
    """
    banditSims = []
    paramDict["arm scheme"] = ("random-excluded",None)
    paramDict["num maps"] = 50
    banditSims.append(BanditSimulator(paramDict))
    banditSims[-1].setName("thread 1")
    banditSims[-1].start()

    #change params and run another
    paramDict["arm scheme"] = ("random-excluded",None)
    paramDict["num maps"] = 300
    banditSims.append(BanditSimulator(paramDict))
    banditSims[-1].setName("thread 2")
    banditSims[-1].start()

    
    for b in banditSims:
        b.join()
        plotRegret(b.armMeans,b.results,str(b.paramDict),b.paramDict["algorithms"],b.optAvg,b.optIndex)
    plt.show()




