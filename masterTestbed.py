from banditPlayers import BanditPlayer
from armModel import TeamTaskModel, NaiveArmModel
import numpy as np

DEBUG = True

if __name__ == "__main__":
    print "Running master testbed for bandits"

    #seed
    np.random.seed(100)
    
    ARM_SCHEME = "random"
    #alg list
    algorithms = ["MA-TS","UCB1","naive-TS"]

    #params for MA-TS
    latentDim = 2
    skillDim = 4
    numMaps = 10
    ttmResolution = 0.1

    #params for naive-TS
    ntsResolution = 0.01

    #general parameters
    trials = 10
    horizon = 100
    numArms = 5
    teamSize = 5

    """
    Team Task Model - create once
    contains all potential parameterizations of the team task model
    """
    ttm = TeamTaskModel(latentDim, skillDim, numMaps,ttmResolution, numArms)
    nam = NaiveArmModel(ntsResolution, numArms)

    bp = {}

    for cur_trial in range(trials):

        #TODO: generate arm parameters, i.e. team members' skill vectors
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

        for a in algorithms:
            if (DEBUG):
                print "(trial ",cur_trial,": time 0) - initialize algorithm ",a

            #model aware thompson sampling
            if (a == "MA-TS"):
                bp[a] = BanditPlayer(a)
                bp[a].initMATS(ttm)
            #naive (model-free) thompson sampling
            elif (a == "naive-TS"):
                bp[a] = BanditPlayer(a)
                bp[a].initNaiveTS(nam)
            elif (a == "UCB1"):
                # do nothing
                bp[a] = BanditPlayer(a)
                bp[a].initUCB1(numArms)
            else:
                print "Algorithm type ", a, " does not exist"

        armSelection = []
        for t in range(horizon):
            print "(trial ",cur_trial,": time ",t,")"

            #use the true model to generate random rewards (may or may not be observed)
            rewards = ttm.generateAllArmRewards(horizon)

            for a in algorithms:
                chosenArm = (bp[a]).chooseNextArm(t)
                if (DEBUG):
                    print "Choosing arm ",chosenArm," for alg ",a

                (bp[a]).updateRewards(chosenArm,rewards[chosenArm])



    print "Finished master testbed"
