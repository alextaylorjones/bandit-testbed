
"""
This class holds all bandit policies and is accessed to make arm selection decisions
"""
class BanditPlayer:

    name = "NONAME"
    armStatsUCB = []
    armModel = None

    def __init__(self,name):
        self.name = name
        if (name == "MA-TS"):
            print "",
        elif (name == "naive-TS"):
            print "",
        elif (name == "UCB1"):
            print "",
        else:
            print "No bandit policy with that name"

    #initialize model aware thompson sampling
    def initMATS(self,teamTaskModel):
        print "Init MA-TS"
        #
        self.armModel = teamtaskModel


    def initNaiveTS(self,naiveArmModel):
        print "Init Naive-TS"
        self.armModel = naiveArmModel


    def initUCB1(self,numArms):

        #no arm model class
        for i in range(numArms):
            #(Num Plays, Empirical Mean)
            self.armStatsUCB.append([0,0])

    def chooseNextArm(self,t):
        print "Choosing next arm"
        if (self.name == "MA-TS"):

            s = np.random.uniform()
            total_weight = 0

            for p in armModel.getParamSpace():
                w = p[2]
                total_weight = total_weight + w
                if (total_weight >= s):
                    sampled_param = p
                    break

            #ensure we made a selection
            assert(sampled_param != None)
            return armModel.getOptArm(sampled_param)

        elif (self.name == "naive-TS"):
            
            sampledParams = []
            for a in armModel.getArms():
                s = np.random.uniform()
                total_weight = 0

                sampledParam = None

                for p in armModel.getParamSpace(a):
                    w = p[1]
                    total_weight = total_weight + w
                    if (total_weight >= s):
                        sampled_param = p
                        break
                assert(sampledParam != None)
                #just append param value to list
                sampledParams.append(sampledParam[1])
                 

            #ensure we made a selection
            assert(sampledParams != [])
            return np.argmin(sampledParams)

        elif (self.name == "UCB1"):
            confidence = []
            i = 0
            for (numPlays,armMean) in self.armStatsUCB:
                #make sure all arms played at least once
                if (numPlays == 0):
                    return i

                confidence.append(armMean + float(math.sqrt(2* math.log(t)/numPlays)))
                i = i + 1

            return np.argmin(confidence)
        else:
            print "Error: No bandit player policy with name",self.name
            return None


    def updateModel(self,armIndex,rewardValue):
        print "Update observed rewards"
        if (self.name == "UCB1"):
            #get total rewards up to now
            prevReward = (self.armStatsUCB[armIndex])[1] * self.armStatsUCB[armIndex][0]
            #add new reward to get complete total 
            newReward = (prevReward + rewardValue)
            #inc arm play count
            self.armStatsUCB[armIndex][0] = self.armStatsUCB[armIndex][0] + 1
            #update empirical mean
            self.armStatsUCB[armIndex][1] = newReward / self.armStatsUCB[armIndex][0]
        elif (self.name == "MA-TS"):
            expSuccessRates = armModel.getSuccessRateDict()

            if (rewardValue == 0):
                for j,(x,M,w) in enumerate(self.armModel.getParamSpace()):
                    w = w * (1- expSuccessRates[(armIndex,j)])
            elif (rewardValue == 1):
                for j,(x,M,w) in enumerate(self.armModel.getParamSpace()):
                    w = w * expSuccessRates[(armIndex,j)]
            else:
                print "Thought these were bernoulli rvs?"
                assert(False)

        elif (self.name == "naive-TS"):
            if (rewardValue == 0):
                for a in self.armModel.getArms():
                    for p,w in self.armModel.getParamSpace(a):
                        w = w * (1-p)
            elif (rewardValue == 1):
               for a in self.armModel.getArms():
                    for p,w in self.armModel.getParamSpace(a):
                        w = w * p
        else:
            print "ERROR: No policy with name ", self.name

