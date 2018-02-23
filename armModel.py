import math
import numpy as np

DEBUG = False

class TeamTaskModel:

    teamSkills = []
    taskLocations = []
    mapLocations = []
    paramSpace = []
    trueModelSpecs = {}
    numArms = None

    def __init__(self, LATENT_DIM, SKILL_DIM, NUM_MAPS, RES,NUM_ARMS):

        #note: hardcoded
        taskLocations = []
        if (LATENT_DIM == 2):
            for x in range(0,int(math.floor(2.0/RES))):
                for y in range(0,int(math.floor(2.0/RES))):
                    taskLocations.append((RES*x-1.0,RES*y-1.0))
                    
        assert(len(taskLocations)>0) #ensure task location creation sanity

        if (DEBUG):
            print "Task locations",taskLocations

        
        # maplocations
        #  
        mapLocations = []
        for x in range(NUM_MAPS):
            A = np.random.normal(size=(SKILL_DIM,LATENT_DIM))
            Q,R = np.linalg.qr(A)
            mapLocations.append(Q)



        #Uniform prior
        unifVal = 1.0/ float(len(taskLocations)*len(mapLocations))

        # Create parameter space
        paramSpace = []
        for x in taskLocations:
            for M in mapLocations:
                paramSpace.append((x,M,unifVal))

        assert(len(paramSpace) > 0)

        if (DEBUG):
            print "Successfully created non-empty parameter space"

        self.taskLocations = taskLocations
        self.mapLocations = mapLocations
        self.paramSpace = paramSpace
        
    def addTeamSkills(self,teams):
        #team is a (skill_dim,team_size) matrix
        self.teamSkills = teams

    #TODO: add capability of non-random selection
    def selectTrueModel(self):
        #TODO: select randomly
        i = np.random.randint(low=0,high=len(taskLocations))
        self.trueModelSpecs["task"] = taskLocations[i]

        i = np.random.randint(low=0,high=len(mapLocations))
        self.trueModelSpecs["map"] = mapLocations[i]


    def generateAllArmRewards(self):
        #setup arm rewards
        if (rewardRVs == None):
        
class NaiveArmModel:

    armParams = {}

    def __init__(self,resolution,numArms):

        assert( 0 <= resolution and 1 >= resolution)

        # each arms has list of potential parameters of arm observation/reward distributions 
        for a in range(numArms):
            self.armParams[a] = np.arange(0,1+resolution,resolution)






