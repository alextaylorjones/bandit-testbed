import numpy as np
import math
"""
This class holds all bandit policies and is accessed to make arm selection decisions
"""
DEBUG = True

class BanditPlayer:

    name = "NONAME"
    armStatsUCB = []
    armModel = None
    numArms = None

    def __init__(self,name,numArms):
        self.name = name
        self.numArms = numArms
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
        self.armModel = teamTaskModel


    def initNaiveTS(self,naiveArmModel):
        print "Init Naive-TS"
        self.armModel = naiveArmModel


    def initUCB1(self):
        self.armStatsUCB = []
        #no arm model class
        assert(self.numArms != None)
        for i in range(self.numArms):
            #(Num Plays, Empirical Mean)
            self.armStatsUCB.append([0,0])

    def chooseNextArm(self,t):
        print "Choosing next arm"
        if (self.name == "MA-TS"):

            s = np.random.uniform()
            total_weight = 0
            sampled_param = None

            for i,p in enumerate(self.armModel.getParamSpace()):
                #params are (task,map,weight) lists
                w = p[2]
                total_weight = total_weight + w
                if (total_weight >= s):
                    sampled_param = i
                    break

            #ensure we made a selection
            assert(sampled_param != None)
            return self.armModel.optTeamParamMap[sampled_param]

        elif (self.name == "naive-TS"):
            
            sampledParams = np.zeros(len(self.armModel.getArms()))

            for a in self.armModel.getArms():
                #if (DEBUG):
                    #print "Param Space Arm ",a,", = ",self.armModel.getParamSpace(a)
                s = np.random.uniform()
                total_weight = 0

                sampled_param = None

                for p in self.armModel.getParamSpace(a):
                    w = p[1]
                    total_weight = total_weight + w
                    if (total_weight >= s):
                        sampled_param = p
                        break

                if (sampled_param == None):
                    print "Fatal error: didnt choose a param in naive-TS"
                    print "rand val = ",s, " - total weight = ",total_weight
                    exit()
                #just append param value to list
                sampledParams[a] = sampled_param[0]
                 

            #ensure we made a selection
            assert(sampledParams != [])
            if (DEBUG):
                print "naive-TS params are :",sampledParams

            #randomly choose an arm with highest param, aka highest mean
            firstMaxIndex = np.argmax(sampledParams)
            allIndices = (np.where(sampledParams == sampledParams[firstMaxIndex]))[0]
            assert(len(allIndices) > 0)
            randMaxIndex = np.random.randint(0,high=len(allIndices))
            return allIndices[randMaxIndex]

        elif (self.name == "UCB1"):
            confidence = []
            i = 0

            #Calculate confidence intervals
            for (numPlays,armMean) in self.armStatsUCB:
                #make sure all arms played at least once
                if (numPlays == 0):
                    return i
                confidence.append(armMean + float(math.sqrt(2* math.log(t+3)/numPlays)))
                i = i + 1

            return np.argmax(confidence)
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
            self.armStatsUCB[armIndex][1] = float(newReward )/ self.armStatsUCB[armIndex][0]
        elif (self.name == "MA-TS"):
            expSuccessRates = self.armModel.getSuccessRateTuple()
            paramList = self.armModel.getParamSpace()
            totalWeight = 0.0
            if (rewardValue == 0):
                for j,(x,M,w) in enumerate(paramList):
                    #recode team,param into expSuccessRate list index
                    paramList[j][2] = paramList[j][2] * (1- expSuccessRates[j*self.numArms + armIndex])
                    totalWeight = totalWeight + paramList[j][2]
            elif (rewardValue == 1):
                for j,(x,M,w) in enumerate(self.armModel.getParamSpace()):
                    #recode team,param into expSuccessRate list index
                    paramList[j][2] = paramList[j][2]* expSuccessRates[j*self.numArms + armIndex]
                    totalWeight = totalWeight + paramList[j][2]
            else:
                print "Thought these were bernoulli rvs?"
                assert(False)
            
            track = [0.0 for _ in range(self.numArms)]

            #normalize to prob distribution
            for j,(x,M,w) in enumerate(paramList):
                paramList[j][2] =  paramList[j][2] /totalWeight
                
                optTeam = self.armModel.optTeamParamMap[j]
                #add model weight to tracker list
                track[optTeam] = track[optTeam] + paramList[j][2]

            print "Track = ",track
            return track



        elif (self.name == "naive-TS"):

            totalWeight = 0.0
            #list of (param, weight) values
            paramList = self.armModel.getParamSpace(armIndex)

            #update weight
            if (rewardValue == 0):
                for i in range(len(paramList)):
                    paramList[i][1] = paramList[i][1] * (1-paramList[i][0])
                    totalWeight = totalWeight + paramList[i][1]
            elif (rewardValue == 1):
                for i in range(len(paramList)):
                    paramList[i][1] = paramList[i][1] * (paramList[i][0])
                    totalWeight = totalWeight + paramList[i][1]
            else:
                print "Thought we were using BRVs"
                assert(0)


            #normalize to prob distribution
            for i in range(len(paramList)):
                paramList[i][1] = paramList[i][1]/totalWeight

        else:
            print "ERROR: No policy with name ", self.name
            assert(0)
        return []
            

