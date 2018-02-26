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
    expSuccessRates = {}
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

        #if (DEBUG):
        #    print "Task locations",taskLocations

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
                paramSpace.append([x,M,unifVal])

        assert(len(paramSpace) > 0)

        if (DEBUG):
            print "Successfully created non-empty parameter space"

        self.taskLocations = taskLocations
        self.mapLocations = mapLocations
        self.paramSpace = paramSpace
        
    def addTeamSkills(self,teams):
        #team is a (skill_dim,team_size) matrix
        self.teamSkills = teams

        #calculate expected success rate for all pts in space
    
        for j,(x,M,w) in enumerate(self.paramSpace):
            #print "Measuring success for param number ",j, "out of ", len(self.paramSpace)
            for i,team in enumerate(teams):
                # mapping team into latent space
                latentImage = np.dot(team,M)

                #find boundaries of box
                lowerBoxBounds = np.min(latentImage,0)
                upperBoxBounds = np.max(latentImage,0)
                
                #print "For this team, true bounds are :",lowerBoxBounds,upperBoxBounds

                successRate = 1.0
                for d in range(self.latentDim):
                    delta = upperBoxBounds[d] - x[d]
                    if (delta < 0.0):
                        successRate = 0
                        break
                    else:
                        #multiply success rate by fractional overlap in dimension d
                        successRate = successRate * min((delta /( upperBoxBounds[d] - lowerBoxBounds[d])),1.0)

                self.expSuccessRates[(i,j)] = successRate

    def getSuccessRateDict(self):
        return self.expSuccessRates

    #TODO: add capability of non-random selection
    def selectTrueModel(self):
        #TODO: select randomly
        i = np.random.randint(low=0,high=len(self.taskLocations))
        self.trueModelSpecs["task"] = self.taskLocations[i]

        i = np.random.randint(low=0,high=len(self.mapLocations))
        self.trueModelSpecs["map"] = self.mapLocations[i]


    
    """
    Calculate true parameter for each team, then generate samples for associated RV
    """
    def generateAllArmRewards(self,horizon):
        self.successMeans = []

        for team in self.teamSkills:
            # mapping team into latent space
            latentImage = np.dot(team,self.trueModelSpecs["map"])

            #find boundaries of box
            lowerBoxBounds = np.min(latentImage,0)
            upperBoxBounds = np.max(latentImage,0)
            
            print "For this team, true bounds are :",lowerBoxBounds,upperBoxBounds

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
        return self.rewardRVs
        if (DEBUG):
            print "Success means : ", self.successMeans

    #model is eleemnt of paramspace (task,map,weight)
    def getOptArm(self,model):
        task = model[0]
        mapping = model[1]

        marginalSuccessMeans = []
        for team in self.teamSkills:
            latentImage = np.dot(team,mapping)

            #find boundaries of box
            lowerBoxBounds = np.min(latentImage,0)
            upperBoxBounds = np.max(latentImage,0)
            
            if (DEBUG):
                print "For this team, true bounds are :",lowerBoxBounds,upperBoxBounds

            successRate = 1.0
            for d in range(self.latentDim):
                delta = upperBoxBounds[d] - (self.trueModelSpecs["task"])[d]
                if (delta < 0.0):
                    successRate = 0
                    break
                else:
                    #multiply success rate by fractional overlap in dimension d
                    successRate = successRate * min((delta /( upperBoxBounds[d] - lowerBoxBounds[d])),1.0)

            marginalSuccessMeans.append(successRate)

        chosenArm = np.argmax(marginalSuccessMeans)
        if (DEBUG):
            print "Optimal arm for sampled model is",chosenArm

        return chosenArm

    def getParamSpace(self):
        return self.paramSpace



class NaiveArmModel:

    armParams = {}
    numArms = None
    def __init__(self,resolution,numArms):

        assert( 0 <= resolution and 1 >= resolution)
        self.numArms = numArms

        # each arms has list of potential parameters of arm observation/reward distributions 
        for a in range(numArms):
            vals = np.arange(0,1+resolution,resolution)
            params = [float(1.0/len(vals))]*len(vals)
            self.armParams[a] = [list(x) for x in zip(vals,params)]

    #gets a list of arm names (for now, ints)
    def getArms(self):
        return range(self.numArms)

    #get list of tuples of (param,weight) for given arm
    def getParamSpace(self,armIndex):
        return self.armParams[armIndex]





