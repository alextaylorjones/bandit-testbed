import matplotlib.pyplot as plt
import math
import operator
from scipy.stats import entropy

#P is success rate of P, sim Q
def getDivBernoulli(P,Q):
    return entropy([P,(1.0-P)],[Q,(1.0-Q)]) 


#Given a team task model and a horizon
def plotUpperRegretBound(ttm,T):
    confidenceDelta = 0.05

    #Calculate Delta for all arms
    teams = ttm.teamSkills
    numTeams= len(teams)
    
    allSuccessRates = ttm.expSuccessRates

    trueSuccessRates = [ttm.getTrueSuccessRate(t) for t in teams]
    deltaList = []
    maxRate = max(trueSuccessRates)
    maxIndex = trueSuccessRates.index(maxRate)


    for r in trueSuccessRates:
        deltaList.append(maxRate - r)
    print "Values of delta are",deltaList
    print "Max arm calculated as",maxIndex

    #Calculate divergence of all models for all arms, average log-likelihood of prior
    #and number of models in Phi and Psi

    pPhi = 0.0
    pPsi = 0.0

    divPhi = [0.0 for _ in teams]
    divPsi = [0.0 for _ in teams]

    weightPhi = 0.0
    weightPsi = 0.0

    numPhi = 0
    numPsi = 0

    print "Iterating models to calculate terms needed for upper bounds"
    for i,(x,M,weight) in enumerate(ttm.paramSpace):
        
        #Get opt team
        optTeam = ttm.optTeamParamMap[i]

        if (optTeam == maxIndex): #Psi
            weightPsi = weightPsi + weight
            numPsi = numPsi +1
            divPsi = [(divPsi[j] + getDivBernoulli(allSuccessRates[i*numTeams + j],trueSuccessRates[j])) for j in range(numTeams)]

            pPsi = pPsi + math.log(weight)

        else: #Phi
            weightPhi = weightPhi + weight
            numPhi = numPhi +1
            divPhi = [(divPhi[j] + getDivBernoulli(allSuccessRates[i*numTeams + j],trueSuccessRates[j])) for j in range(numTeams)]

            pPhi = pPhi + math.log(weight)

    
    assert(numPhi > 0 and numPsi>0)

    pPhi = pPhi / numPhi
    divPhi = [(float(d) / numPhi) for d in divPhi]

    pPsi = pPhi / numPhi
    divPsi = [(float(d) / numPsi) for d in divPsi]


    print "Bound variables\n\n\n"
    print "For Opt(Psi) Models -  LogProb Prior %f, Cardinality %i" % (pPsi,numPsi)
    print "Arm Divergence Averages",divPsi,"\n\n"
    print "For Subopt(Phi) Models - LogProb Prior %f, Cardinality %i" % (pPhi,numPhi)
    print "Arm Divergence Averages",divPhi

    quit()
    #Calculate Phi and Psi
    #For each t<T
    print "Calculating optimization problem over all times"
    const = pPsi - pPhi - math.log(numPsi/float(numPhi)) - math.log ( math.log(1.0/confidenceDelta**2))
    for t in range(T):
        if (t == T/t):
            print "Halfway done with times"
        #Calculate

        #Determine if there is a solution to optimization prob of theorem 2, 
        #Store solution

    #Plot solution




