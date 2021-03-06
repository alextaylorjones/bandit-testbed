import math
import numpy as np

DEBUG = True
EPSILON = 0.005

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
        self.numArms = NUM_ARMS

        #note: hardcoded
        taskLocations = []
        if (LATENT_DIM == 2):
            for x in range(0,int(math.floor(2.0/PT_RES))):
                for y in range(0,int(math.floor(2.0/PT_RES))):
                    taskLocations.append((PT_RES*x-1.0,PT_RES*y-1.0))

            taskLocations.append(np.zeros(LATENT_DIM))

        #generate all unique rotations

        """
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
        """



        assert(len(taskLocations)>0) #ensure task location creation sanity

        #if (DEBUG):
        #    print "Task locations",taskLocations

        # maplocations
        #
        mapLocations = []
        for x in range(NUM_MAPS):
            A = np.random.uniform(size=(SKILL_DIM,LATENT_DIM))
            Q,R = np.linalg.qr(A)
            mapLocations.append(Q)

        mapLocations.append(np.eye(SKILL_DIM,LATENT_DIM))


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

    def evenDecisionReweight(self):

        decisionWeights = [0.0 for i in range(self.numArms)]

        #calculate decision weights
        for j,(_,_,w) in enumerate(self.paramSpace):
            optTeam =  self.optTeamParamMap[j]
            decisionWeights[optTeam] = decisionWeights[optTeam] + w

        d = float(1.0/self.numArms)
        for j,(_,_,w) in enumerate(self.paramSpace):
            optTeam =  self.optTeamParamMap[j]
            self.paramSpace[j][2] = self.paramSpace[j][2] * float(d/decisionWeights[optTeam])

        if (DEBUG):
            print "Evenly reweighted decision regions"

            decisionWeights = [0.0 for i in range(self.numArms)]

            #calculate decision weights
            for j,(_,_,w) in enumerate(self.paramSpace):
                optTeam =  self.optTeamParamMap[j]
                decisionWeights[optTeam] = decisionWeights[optTeam] + w
            print "DECISION WEIGHTS: ",decisionWeights



    def addTeamSkills(self,teams):
        #team is a (skill_dim,team_size) matrix
        self.teamSkills = teams
        self.optTeamParamMap = []

        #calculate expected success rate for all pts in space
        if (DEBUG):
            print "Beginning calculation of all success rates ....",
        for j,(x,M,w) in enumerate(self.paramSpace):
            #print "Measuring success for param number ",j, "out of ", len(self.paramSpace)
            optTeam = None
            maxSuccessRate = 0.0
            for i,team in enumerate(teams):
                # mapping team into latent space
                latentImage = np.dot(team,M)

                #find boundaries of box
                lowerBoxBounds = np.min(latentImage,0)
                upperBoxBounds = np.max(latentImage,0)
                #print "For team ",i," bounds are :",lowerBoxBounds,upperBoxBounds

                successRate = 1.0
                for d in range(self.latentDim):
                    #add extra term due to discrete space
                    delta = upperBoxBounds[d] - x[d]

                    if (delta < 0.0):
                        successRate = EPSILON
                        break
                    else:
                        #multiply success rate by fractional overlap in dimension d
                        successRate = successRate * min((delta /( upperBoxBounds[d] - lowerBoxBounds[d])),1.0)
                if (successRate == 1.0):
                    successRate = 1.0 - EPSILON

                if (maxSuccessRate <= successRate):
                    optTeam = i
                    maxSuccessRate = successRate
                self.expSuccessRates.append(successRate)

            #sanity (some team has non-zero success rate
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
    def selectTrueModel(self,exclude=False,mapping=None,task=None):
        #TODO: select randomly


        if ((mapping == None) ^ (task == None)):
            print "Trying to explicitly assign team-task model, but only one given"
            assert(0)

        #explicit assignment
        if (mapping !=None and task != None):
            print "Explicit assignment of mapping-task pair = ",mapping,task
            self.trueModelSpecs["task"] = task
            self.trueModelSpecs["map"] = mapping
            return

        if (exclude == False):
            i = np.random.randint(low=0,high=len(self.taskLocations))
            self.trueModelSpecs["task"] = self.taskLocations[i]

            i = np.random.randint(low=0,high=len(self.mapLocations))
            self.trueModelSpecs["map"] = self.mapLocations[i]
            return
        else:
            #generate map outside params
            A = np.random.normal(size=(self.skillDim,self.latentDim))
            Q,R = np.linalg.qr(A)
            self.trueModelSpecs["map"] = Q

            #generate task randomly
            i = np.random.randint(low=0,high=len(self.taskLocations))
            self.trueModelSpecs["task"] = self.taskLocations[i]
            return


    def getTrueSuccessRate(self,team):
        assert("map" in self.trueModelSpecs.keys() and "task" in self.trueModelSpecs.keys())

        latentImage = np.dot(team,self.trueModelSpecs["map"])
        lowerBoxBounds = np.min(latentImage,0)
        upperBoxBounds = np.max(latentImage,0)
        successRate = 1.0
        for d in range(self.latentDim):
            # since we are in discrete space, count equal overlap as single segment
            delta = upperBoxBounds[d] - (self.trueModelSpecs["task"])[d]
            if (delta < 0.0):
                successRate = EPSILON
                break
            else:
                #multiply success rate by fractional overlap in dimension d
                successRate = successRate * min((delta /( upperBoxBounds[d] - lowerBoxBounds[d])),1.0)
        return successRate




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

            print "For team ",i,", true bounds (min,max) are :",lowerBoxBounds,upperBoxBounds

            successRate = 1.0
            for d in range(self.latentDim):
                # since we are in discrete space, count equal overlap as single segment
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


#task pt is k dimensions
# box coorindates is 2*k arrray
def getSuccessProb(taskPt,boxCoordinates):
    assert(len(taskPt)*2 == len(boxCoordinates))
    prob = 1.0
    for i,c in enumerate(taskPt):
        mn,mx = boxCoordinates[(2*i):(2*i+2)]
        assert(mn < mx)
        d = mx - mn
        if (mx < taskPt[i]):
            prob = EPSILON
            return prob
        elif (mn > taskPt[i]):
            continue
        else:
            prob = prob * (mx-taskPt[i])/d
    if (prob > 1.0-EPSILON):
        prob = 1.0 - EPSILON
    if (prob < EPSILON):
        prob = EPSILON
    return prob

class NaiveArmModel:

    armParams = {}
    numArms = None
    resolution = -1
    optTeamParamMap = []
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
