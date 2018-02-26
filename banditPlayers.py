
"""
This class holds all bandit policies and is accessed to make arm selection decisions
"""
class BanditPlayer:

    name = "NONAME"

    def __init__(self,name):
        self.name = name
        if (name == "MA-TS"):
            continue
        elif (name == "naive-TS"):
            continue
        else:
            print "No bandit policy with that name"

    #initialize model aware thompson sampling
    def initMATS(self,teamTaskModel):
        print "Init MA-TS"


    def initNaiveTS(self,naiveArmModel):
        print "Init Naive-TS"

    def initUCB1(self,

    def chooseNextArm(self):
        print "Choose next arm"



    def updateRewards(self,armIndex,rewardValue):
        print "Update rewards"

