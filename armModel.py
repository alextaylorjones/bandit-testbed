import math
import numpy as np

DEBUG = True

class TeamTaskModel:

    successMeans = []
    rewardRVs = []
    latentDim = None
    skillDim = None
    teamSkills = []
    taskLocations = []
    taskResolution = None
    rotResolution = None
    mapLocations = []
    paramSpace = []
    trueModelSpecs =  {}
    expSuccessRates = []
    optTeamParamMap = []
    numArms = None

    def __init__(self, LATENT_DIM, SKILL_DIM, NUM_MAPS, PT_RES,ANGLE_RES,NUM_ARMS):

        self.latentDim = LATENT_DIM
        self.skillDim = SKILL_DIM
        self.taskResolution = PT_RES
        self.rotResoluton = ANGLE_RES

        #note: hardcoded
        taskLocations = []
        if (LATENT_DIM == 2):
            for x in range(0,int(math.floor(2.0/RES))):
                for y in range(0,int(math.floor(2.0/RES))):
                    taskLocations.append((RES*x-1.0,RES*y-1.0))

        #generate all unique rotations

        # initial basis
        gen = np.eye(skillDim,latentDim)

        #Rot*gen = rotated matrix
        #exp(r * u ^ v) gen ->

        #make sure resolution is even
        numRots = int(math.pi/ANGLE_RES)

        #cannot have resolution more than 90 degrees
        assert (numRots > 0)

        totalRots = math.pow(numRots,self.latentDim - 1)

        if (DEBUG):
            print "Total number of rotations is ",totalRots
            if (totalRots > 1000):
                print "More than ten thousand rotations, may take a long time..."
        rotList = [gen]

        for index in range(int(totalRots)):
            if (index % numRots == 0):
                m = index / numRots
                #STOPPED HERE



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

    
    def reset(self):
        #reset weights to uniform weights
        unifValue = float(1.0/len(self.paramSpace))
        for i in range(len(self.paramSpace)):
            self.paramSpace[i][2] = unifValue

        print "Resetting param values in team task model"

    def addTeamSkills(self,teams):
        #team is a (skill_dim,team_size) matrix
        self.teamSkills = teams

        #calculate expected success rate for all pts in space
    
        if (DEBUG):
            print "Begining calculation of all success rates ....",
        for j,(x,M,w) in enumerate(self.paramSpace):
            #print "Measuring success for param number ",j, "out of ", len(self.paramSpace)
            optTeam = None
            maxSuccessRate = -1
            for i,team in enumerate(teams):
                # mapping team into latent space
                latentImage = np.dot(team,M)

                #find boundaries of box
                lowerBoxBounds = np.min(latentImage,0)
                upperBoxBounds = np.max(latentImage,0)
                
                #print "For this team, true bounds are :",lowerBoxBounds,upperBoxBounds

                successRate = 1.0
                for d in range(self.latentDim):
                    #add extra term due to discrete space
                    delta = upperBoxBounds[d] - x[d] + self.taskResolution
                    if (delta < 0.0):
                        successRate = 0
                        break
                    else:
                        #multiply success rate by fractional overlap in dimension d
                        successRate = successRate * min((delta /( upperBoxBounds[d] - lowerBoxBounds[d])),1.0)

                if (maxSuccessRate < successRate):
                    optTeam = i
                    maxSuccessRate = successRate
                self.expSuccessRates.append(successRate)

            #sanity
            assert(optTeam != None)

            #save which team is optimal for parameter j
            self.optTeamParamMap.append(optTeam)
            
                #old 
                #self.expSuccessRates[(i,j)] = successRate
        if (DEBUG):
            print "Successfully calculate all success rates"

    def getSuccessRateTuple(self):
        return self.expSuccessRates

    #TODO: add capability of non-random selection
    def selectTrueModel(self,exclude=False):
        #TODO: select randomly

        if (exclude == False):
            i = np.random.randint(low=0,high=len(self.taskLocations))
            self.trueModelSpecs["task"] = self.taskLocations[i]

            i = np.random.randint(low=0,high=len(self.mapLocations))
            self.trueModelSpecs["map"] = self.mapLocations[i]
        else:
            #generate map outside params 
            A = np.random.normal(size=(self.skillDim,self.latentDim))
            Q,R = np.linalg.qr(A)
            self.trueModelSpecs["map"] = Q

            #generate task randomly
            i = np.random.randint(low=0,high=len(self.taskLocations))
            self.trueModelSpecs["task"] = self.taskLocations[i]

    
    """
    Calculate true parameter for each team, then generate samples for associated RV
    """
    def generateAllArmRewards(self,horizon):
        self.successMeans = []
        self.rewardRVs = []

        for i,team in enumerate(self.teamSkills):
            # mapping team into latent space
            latentImage = np.dot(team,self.trueModelSpecs["map"])

            #find boundaries of box
            lowerBoxBounds = np.min(latentImage,0)
            upperBoxBounds = np.max(latentImage,0)
            
            print "For team ",i,", true bounds are :",lowerBoxBounds,upperBoxBounds

            successRate = 1.0
            for d in range(self.latentDim):
                # since we are in discrete space, count equal overlap as single segment
                delta = upperBoxBounds[d] - (self.trueModelSpecs["task"])[d] + self.taskResolution
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
            print "True Success means : ", self.successMeans
        return self.rewardRVs,self.successMeans

    #model is eleemnt of paramspace (task,map,weight)
    """ #Do not perform recalculation
    def getOptArm(self,model):

        
        task = model[0]
        mapping = model[1]

        marginalSuccessMeans = []
        for team in self.teamSkills:
            latentImage = np.dot(team,mapping)

            #find boundaries of box
            lowerBoxBounds = np.min(latentImage,0)
            upperBoxBounds = np.max(latentImage,0)
            
            #if (DEBUG):
                #print "For this team, true bounds are :",lowerBoxBounds,upperBoxBounds

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
        chosenArm = self.optTeamParamMap[model]

        if (DEBUG):
            print "Optimal arm for sampled team-task model is",chosenArm

        return chosenArm
    """

    def getParamSpace(self):
        return self.paramSpace



class NaiveArmModel:

    armParams = {}
    numArms = None
    resolution = -1
    def __init__(self,resolution,numArms):

        assert( 0 <= resolution and 1 >= resolution)
        self.numArms = numArms
        self.resolution = resolution

        # each arms has list of potential parameters of arm observation/reward distributions 
        for a in range(numArms):
            params = np.arange(0,1+resolution,resolution)
            weights = [float(1.0/len(params))]*len(params)
            self.armParams[a] = [list(x) for x in zip(params,weights)]

    #gets a list of arm names (for now, ints)
    def getArms(self):
        return range(self.numArms)

    #get list of tuples of (param,weight) for given arm
    def getParamSpace(self,armIndex):
        return self.armParams[armIndex]


    #call initializer again
    def reset(self):
        for a in range(self.numArms):
            unifVal = float(1.0/len(self.armParams[a]))
            self.armParams[a] = [[entry[0],unifVal] for entry in self.armParams[a]]

        print "Resetting param values in naive arm model"



