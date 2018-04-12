from banditPlayers import BanditPlayer
from armModel import TeamTaskModel, NaiveArmModel
from resultsTracker import *
import numpy as np
from threading  import Thread
import math

DEBUG = True
EPSILON = 0.05

class BanditSimulator:#(Thread):
    paramDict = {}
    results = None
    decisionRegionTracker = None
    optAvg = None
    optIndex = None
    armMeans = None

    def __init__(self,paramDict):
        #Thread.__init__(self)
        #make a copy
        self.paramDict = paramDict.copy()

    def run(self):
        """
        Unpack params
        """
        paramDict = self.paramDict
        algorithms = paramDict["algorithms"]
        armScheme = paramDict["arm scheme"]
        latentDim =   paramDict["latent dimension"]
        skillDim =  paramDict["skill dimension"]
        numMaps =  paramDict["num maps"]
        ttmResolution= paramDict["model task resolution"]
        rotResolution = paramDict["rotation resolution"]
        ntsResolution =  paramDict["naive param resolution"]
        trials =  paramDict["trials"]
        horizon =  paramDict["horizon"]
        numArms =  paramDict["num arms"]
        teamSize =  paramDict["team size"]

        #printing options
        np.set_printoptions(precision=3)
        """
        Team Task Model - create once
        contains all potential parameterizations of the team task model
        """
        ttm = TeamTaskModel(latentDim, skillDim, numMaps,ttmResolution, rotResolution,numArms)
        nam = NaiveArmModel(ntsResolution, numArms)

        bp = {}

        #one result list for each algorithm
        results = [[] for _ in algorithms]
        #one model tracker list for each algorithm
        tracker = [[] for _ in algorithms]

        #done once for all trials
        #select team locations, task and mapping
        teams = []


        if (armScheme[0] == "random"):
            if (armScheme[1] == None):
                for _ in range(numArms):
                    team = np.random.uniform(low=-1.0,high=1.0,size=(teamSize,skillDim))
                    teams.append(team)

                #Add skill matrices for teams
                ttm.addTeamSkills(teams)

                #note: currently random choice over all potential models
                ttm.selectTrueModel()
            elif (armScheme[1] == "well-spaced"):
                #select true model
                ttm.selectTrueModel()

                #randomly select teams until we fill each mean bucket
                meanBuckets = [None for _ in range(numArms)]
                filledBuckets = 0
                width = 1.0/numArms
                while (filledBuckets < len(meanBuckets)):
                    #generate random team
                    team = np.random.uniform(low=-1.0,high = 1.0,size=(teamSize,skillDim))

                    #see if bucket is filled
                    m = ttm.getTrueSuccessRate(team)
                    bucketID = int(math.floor(m / width))-1
                    if (meanBuckets[bucketID] == None):
                        filledBuckets = filledBuckets + 1
                        if (DEBUG):
                            print "Filling ",filledBuckets, " out of ",len(meanBuckets), "buckets"
                        #fill bucket if not team in bucket
                        meanBuckets[bucketID] = team

                ttm.addTeamSkills(meanBuckets)

            elif (armScheme[1] == "clustered"):

                numClusters = armScheme[2]
                allTeams = []
                assert(numClusters > 0)
                #select true model
                ttm.selectTrueModel()

                #randomly select teams until we fill each mean bucket
                meanBuckets = [None for _ in range(numClusters)]
                filledBuckets = 0
                MAX_SUCCESS = 0.9
                width = float(MAX_SUCCESS/numClusters)
                while (filledBuckets < len(meanBuckets)):
                    #generate random team
                    team = np.random.uniform(low=-1.0,high = 1.0,size=(teamSize,skillDim))
                    #see if bucket is filled
                    m = ttm.getTrueSuccessRate(team)
                    if (m <= 0.01 or m > MAX_SUCCESS):
                        continue
                    bucketID = int(math.ceil(m / width))-1
                    print "Bucket ID", bucketID
                    if (meanBuckets[bucketID] is None):
                        filledBuckets = filledBuckets + 1
                        if (DEBUG):
                            print "Filling ",filledBuckets, " out of ",len(meanBuckets), "buckets"
                        #fill bucket if not team in bucket
                        meanBuckets[bucketID] = team

                # each bucket is a landmark,
                #other teams are built close to that team
                orderedTeams = []
                for team in meanBuckets:
                    orderedTeams.append(team)
                    print "Original team: ", team
                    #wiggle team
                    for i in range(int(numArms/numClusters)-1):
                        epsilonShift = EPSILON*np.random.uniform(teamSize,skillDim)
                        shiftedTeam = team + epsilonShift
                        orderedTeams.append(shiftedTeam)
                        print "New team: ",shiftedTeam


                if (DEBUG):
                    assert(len(orderedTeams) == numArms)
                #add all teams to model
                ttm.addTeamSkills(orderedTeams)


            else:
                print "Incorrect subscheme for random",armScheme
                assert(0)


        elif (armScheme[0] == "random-excluded"):
            for _ in range(numArms):
                team = np.random.uniform(low=-1.0,high=1.0,size=(teamSize,skillDim))
                teams.append(team)

            #Add skill matrices for teams
            ttm.addTeamSkills(teams)

            #note: currently random choice over all potential models
            ttm.selectTrueModel(exclude=True)
        elif (armScheme[0] == "space-util-example"):
            #let mapping be eye
            assert(teamSize  > 1)

            mapping = np.eye(skillDim,latentDim)
            task = np.zeros(latentDim)
            teams= []
            #arrange all teams along single dimension
            if (armScheme[1] == "single-dim"):
                armMeans = np.arange(0.0,1.0 + 1.0/numArms, 1.0/numArms)
                heights = np.random.uniform(low=1.0,high=2.0,size=numArms)
                for i in range(numArms):
                    #init team matrix
                    teamMat = np.zeros((teamSize,skillDim))

                    #skewer along 2nd dimension
                    teamMat[0][1] = np.random.uniform()

                    for r in range(1,teamSize):
                        teamMat[r][1] =np.random.uniform()

                    #give volume in all remaining dimensions, but all dominating task
                    for d in range(2,latentDim):
                        a = np.random.uniform(2)
                        teamMat[0][d] = min(a)
                        teamMat[1][d] = max(a)
                        assert(min(a) < max(a))

                    #this much of the volume should extend above the dim 0 axis
                    f = heights[i] * armMeans[i]

                    #individual 1 has skill f
                    teamMat[0][0] = f
                    #individual 2 has skill f-height
                    teamMat[1][0] = f - heights[i]
                    #all remaining individuals have 0 skill

                    #save team
                    teams.append(teamMat)

                    print "Team ",i," has matrix \n", teamMat

            #arrange teams along all dimensions
            elif (armScheme[1] == "all-dim"):
                armMeans = np.arange(0.0,1.0 + 1.0/numArms, 1.0/numArms)
                heights = np.random.uniform(low=1.0,high=2.0,size=numArms)

                for i in range(numArms):
                    #choose dimensions to skewer on
                    skewerDim = i % latentDim
                    #choose dimension to vary height upon
                    varyDim = (skewerDim + 1 ) % latentDim

                    #STOPPED HERE
                    #init team matrix
                    teamMat = np.zeros((teamSize,skillDim))

                    #skewer along skewer dimension
                    teamMat[0][skewerDim] = np.random.uniform()
                    for r in range(1,teamSize):
                        teamMat[r][skewerDim] = np.random.uniform()

                    #give volume in all remaining dimensions, but all dominating task
                    for d in range(latentDim):
                        if (d == skewerDim or d == varyDim):
                            continue
                        a = np.random.uniform(2)
                        teamMat[0][d] = min(a)
                        teamMat[1][d] = max(a)
                        assert(min(a) < max(a))



                    #this much of the volume should extend above the dim vary dimension axis
                    f = heights[i] * armMeans[i]

                    #individual 1 has skill f
                    teamMat[0][varyDim] = f
                    #individual 2 has skill f-height
                    teamMat[1][varyDim] = f - heights[i]
                    #all remaining individuals have 0 skill

                    #save team
                    teams.append(teamMat)
                    print "Team ",i," has matrix\n", teamMat

            else:
                print "Incorrect second argument to arm scheme ",armScheme
                assert(0)

            #Add skill matrices for teams
            ttm.addTeamSkills(teams)

            ttm.selectTrueModel(mapping=mapping,task=task)
        else:
            print "No arm scheme by name",
            print armScheme
            assert(False)



        if (len(armScheme) > 2):
            """
                Reweight models so decision regions are equally weighted
            """
            if (armScheme[2] == "re-weight"):
                if (DEBUG):
                    print "\n\n\n******\n Reweight decision regions for even first selection"
                ttm.evenDecisionReweight()


        for cur_trial in range(trials):
            if (DEBUG):
                print "Starting trial ",cur_trial

            for i in range(len(algorithms)):
                results[i].append([])
                tracker[i].append([])

            #TODO: generate arm parameters, i.e. team members' skill vectors
            for a in algorithms:
                if (DEBUG):
                    print "(trial ",cur_trial,": time 0) - initialize algorithm ",a

                #model aware thompson sampling
                if (a == "MA-TS"):
                    bp[a] = BanditPlayer(a,numArms)
                    bp[a].initMATS(ttm)
                    ttm.reset() # reset param weights
                    ttm.evenDecisionReweight()
                #naive (model-free) thompson sampling
                elif (a == "naive-TS"):
                    bp[a] = BanditPlayer(a,numArms)
                    bp[a].initNaiveTS(nam)
                    nam.reset() #reset param weights
                elif (a == "UCB1"):
                    # do nothing
                    bp[a] = BanditPlayer(a,numArms)
                    bp[a].initUCB1()
                else:
                    print "Algorithm type ", a, " does not exist"

            armSelection = []
            #use the true model to generate random rewards (may or may not be observed)
            rewards,armMeans = ttm.generateAllArmRewards(horizon)

            #sanity check for no arm fouling between trials
            """
            if (self.armMeans != None):
                assert(armMeans == self.armMeans)
            """

            #Save arm reward means
            if (self.armMeans == None):
                self.armMeans = armMeans
            else: #ensure that these means dont change in between trials
                """
                assert(self.armMeans == armMeans)
                """

            for t in range(horizon):
                print "(trial ",cur_trial,": time ",t,")"



                for i,a in enumerate(algorithms):
                    chosenArm = (bp[a]).chooseNextArm(t)
                    if (DEBUG):
                        print "Choosing arm ",chosenArm," for alg ",a
                    #update model and track arm model weight for this iteration
                    track = (bp[a]).updateModel(chosenArm,rewards[chosenArm][t])
                    tracker[i][-1].append(track)

                    """ Calculate the weight of decision region of optimal """
                    #take the results for arm a, taking the latest trial list
                    results[i][-1].append((chosenArm,rewards[chosenArm][t]))

        optAvg = max(ttm.successMeans)
        optIndex = np.argmax(ttm.successMeans)

        #save results in class variables
        self.results = results
        self.decisionRegionTracker = tracker
        self.optAvg = optAvg
        self.optIndex = optIndex

        if (DEBUG):
            print "ARM MEANS: ",self.armMeans



if __name__ == "__main__":
    print "Running master testbed for bandits"

    #seed
    np.random.seed(730)

    armScheme = ("random",None)
    #armScheme = ("space-util-example","all-dim")
    #alg list
    algorithms = ["naive-TS","MA-TS","UCB1"]

    #params for MA-TS
    latentDim = 2
    skillDim = 4
    numMaps = 250
    ttmResolution = 0.1
    rotResolution = math.pi/2.0 #45 deg.

    #params for naive-TS
    ntsResolution = 0.05

    #general parameters
    trials = 5
    horizon = 150
    numArms = 18
    teamSize = 2

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
    paramDict["rotation resolution"] = rotResolution
    paramDict["naive param resolution"] = ntsResolution
    paramDict["trials"] = trials
    paramDict["horizon"] = horizon
    paramDict["num arms"] = numArms
    paramDict["team size"] = teamSize

    """
    Run test threads
    """
    banditSims = []

    paramDict["arm scheme"] = ("random","clustered",6)
    b = BanditSimulator(paramDict)
    b.run()
    banditSims.append(b)

    #paramDict["arm scheme"] = ("random","clustered",8)
    #banditSims.append(BanditSimulator(paramDict))
    #banditSims[-1].run()

    """
    paramDict["arm scheme"] = ("random","clustered",25)
    banditSims.append(BanditSimulator(paramDict))
    banditSims[-1].setName("thread 2")
    banditSims[-1].start()
    """


    #for b in banditSims:
    #    b.join()
    #    print "Done with one sim."

    clusteredInstances = []
    clusterSizes = []

    for b in banditSims:
        plotRegret(b.results,b.decisionRegionTracker,str(b.paramDict),b.paramDict["algorithms"],b.optAvg,b.optIndex,b.armMeans)
        plotTeamBoxes(b)

        #If clustering was applied, show the posterior mass of the clusters
        if (len(b.paramDict["arm scheme"]) >= 3):
            if (b.paramDict["arm scheme"][1].startswith("clustered")):
                numClusters = b.paramDict["arm scheme"][2]
                numArms = b.paramDict["num arms"]
                if (numArms % numClusters > 0):
                    print "ERROR CANNOT DEAL WITH UNEVEN CLUSTERS NOW"
                    continue
                if (DEBUG):
                    print "Showing cluster posterior masses"
                clusteredInstances.append(b)
                clusterSizes.append(numClusters*[numArms/numClusters])


    print "Before calling plot clusters"
    plotClusterPosteriors(clusteredInstances,clusterSizes,str(b.paramDict))

        #if (b.paramDict["latent dimension"] == 2) :
        #    plotTeamBoxes(b)
