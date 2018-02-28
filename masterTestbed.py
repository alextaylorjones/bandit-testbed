from banditPlayers import BanditPlayer
from armModel import TeamTaskModel, NaiveArmModel
from resultsTracker import plotRegret
import numpy as np

DEBUG = True

if __name__ == "__main__":
    print "Running master testbed for bandits"

    #seed
    np.random.seed(69)
    
    ARM_SCHEME = "random"
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
    horizon = 500
    numArms = 25
    teamSize = 5

    """
    Fill param dictionary with all params
    """

    paramDict["arm scheme"] = ARM_SCHEME
    paramDict["latent dimension"] = latentDim
    paramDict["skill dimension"] = skillDim


def runMasterTest(paramDict):
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
    if (ARM_SCHEME == "random"):
        for _ in range(numArms):
            team = np.random.uniform(low=-1.0,high=1.0,size=(teamSize,skillDim))
            teams.append(team)

        #Add skill matrices for teams
        ttm.addTeamSkills(teams)

        #note: currently random choice over all potential models
        ttm.selectTrueModel()

    else:
        print "No arm scheme by name",
        print ARM_SCHEME
        assert(False)

 
    for cur_trial in range(trials):
              
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
        rewards = ttm.generateAllArmRewards(horizon)

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

    print "Optimal Arm mean was ",optAvg
    print "Finished master testbed"
    s=np.random.randint(0,10000)
    #print "Raw Results:",results
    plotRegret(results,algorithms,optAvg,optIndex)



