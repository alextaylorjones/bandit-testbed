
"""
This class holds all bandit policies and is accessed to make arm selection decisions
"""
class BanditPlayer:

    name = "NONAME"

    def __init__(self,name):
        if (name == "thompson-sampling"):
            self.name = name
        else:
            print "No bandit policy with that name"

    #initialize model aware thompson sampling
    def initMATS(self,teamTaskModel):


    def initNaiveTS(self,naiveArmModel):

    def chooseNextArm(self):



    def updateRewards(self,armIndex,rewardValue):

