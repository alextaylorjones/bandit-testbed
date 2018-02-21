import math

DEBUG = True
SKILL_DIM = 3
LATENT_DIM = 2
RES = 0.1

class TeamTaskModel:

    def __init__(self):

        #note: hardcoded
        taskLocations = []
        if (LATENT_DIM == 2):
            for x in range(0,int(math.floor(1.0/RES))):
                for y in range(0,int(math.floor(1.0/RES))):
                    taskLocations.append((x,y))
                    
        assert(len(taskLocations)>0) #ensure task location creation sanity

        if (DEBUG):
            print "Task locations",taskLocations

        
        #maplocations
        mapLocations = []

        #Uniform prior
        unifVal = 1.0/ float(len(taskLocations)*len(mapLocations))

        # Create parameter space
        paramSpace = []
        for x in taskLocations:
            for M in mapLocations:
                paramSpace.append((x,M,unifVal))

