import math
import numpy as np

DEBUG = True

class TeamTaskModel:

    successMeans = []
    rewardRVs = []
    latentDim = None
    teamSkills = []
    taskLocations = []
    mapLocations = []
    paramSpace = []
    trueModelSpecs = {}
    numArms = None

    def __init__(self, LATENT_DIM, SKILL_DIM, NUM_MAPS, RES,NUM_ARMS):

        self.latentDim = LATENT_DIM
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
        i = np.random.randint(low=0,high=len(self.taskLocations))
        self.trueModelSpecs["task"] = self.taskLocations[i]

        i = np.random.randint(low=0,high=len(self.mapLocations))
        self.trueModelSpecs["map"] = self.mapLocations[i]


    def generateAllArmRewards(self,horizon):
        #setup arm rewards
        if (self.rewardRVs == []):
            for team in self.teamSkills:
                # mapping team into latent space
                latentImage = np.dot(team,self.trueModelSpecs["map"])

                #find boundaries of box
                lowerBoxBounds = np.min(latentImage,0)
                upperBoxBounds = np.max(latentImage,0)
                
                print "For this team, bounds are :",lowerBoxBounds,upperBoxBounds

                successRate = 1.0
                for d in range(self.latentDim):
                    delta = upperBoxBounds[d] - (self.trueModelSpecs["task"])[d]
                    if (delta < 0.0):
                        successRate = 0
                        break
                    else:
                        #multiply success rate by fractional overlap in dimension d
                        successRate = successRate * min((delta /( upperBoxBounds[d] - lowerBoxBounds[d])),1.0)

                self.successMeans.append(successRate)
                s = np.random.binomial(1,successRate,size=(horizon))
                self.rewardRVs.append(s)
            if (DEBUG):
                print "Success means : ", self.successMeans


class NaiveArmModel:

    armParams = {}

    def __init__(self,resolution,numArms):

        assert( 0 <= resolution and 1 >= resolution)

        # each arms has list of potential parameters of arm observation/reward distributions 
        for a in range(numArms):
            self.armParams[a] = np.arange(0,1+resolution,resolution)






