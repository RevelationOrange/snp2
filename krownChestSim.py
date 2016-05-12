import random as rng
from copy import deepcopy


rewards = ['phoenix feather', 'moon stone', 'roaring powder', 'golden silk', 'shadow essence',
           'platinum hammer', 'mystical hourglass', 'magical key', 'krowns']
opened = []
chests = {1:[30, 40], 2:[80, 100], 3:[160, 200]}
useChest = 2
chestCost = chests[useChest][0]
chestBonus = chests[useChest][1]
relWeights = [0, 0, 0, 0, 0, 0, 1, 1, 0]
baseTargets = []
for i in xrange(len(rewards)):
    if relWeights[i]: baseTargets.append([rewards[i], float(relWeights[i])/sum(relWeights)])
print baseTargets
baseChances = 1./len(rewards)
baseKrowns = int(1e6)
ntrials = 1e3
nchestsHist = []
avgnchestsHist = []
targetsHists = [[] for i in baseTargets]
totalTargetsHist = []
avgtargetsHist = []

for i in xrange(int(ntrials)):
    targetsGet = [0 for j in baseTargets]
    krowns = baseKrowns
    while krowns >= chestCost*9:
        chestsOpened = 0
        got = []
        gotn = []
        targets = deepcopy(baseTargets)
        while len(opened) < 9:
            krowns -= chestCost
            chestI = rng.randint(0,8)
            while chestI in opened: chestI = rng.randint(0,8)
            opened.append(chestI)
            if chestI == 8: krowns += chestBonus
            result = rewards[chestI]
            got.append(result)
            gotn.append(chestI)
            chestsOpened += 1
            if opened == [8] or (len(opened) == 2 and 8 in opened): opened = []
            if result in [x[0] for x in targets]: #break
                j = [x[0] for x in baseTargets].index(result)
                targetsGet[j] += 1
                k = [x[0] for x in targets].index(result)
                targets.pop(k)
                remaining = 9 - len(opened)
                if remaining == 0: chances = 0
                else: chances = float(sum([y[1] for y in targets]))/remaining
                #print chances
                # break
                if (len(opened) == 8 and 8 not in opened) or chances > baseChances: pass
                else: break
        nchestsHist.append(chestsOpened)
        #if len(gotn) > 9: print chestsOpened, krowns, gotn
        opened = []
    tHsum = 0
    for x in xrange(len(targetsHists)):
        targetsHists[x].append(targetsGet[x])
        tHsum += targetsGet[x]
    totalTargetsHist.append(tHsum)
    trialAvgChests = float(sum(nchestsHist)) / len(nchestsHist)
    if i%(ntrials/10) == 0:
        print 'average chests opened:', trialAvgChests, '(trial {}/{})'.format(i,ntrials)
        tGsum = 0
        for x in xrange(len(targetsGet)):
            if targetsGet[x] != 0:
                print 'target #{} acq: {}, krowns per target: {}'.format(x+1, targetsGet[x], float(baseKrowns)/targetsGet[x])
            tGsum += targetsGet[x]
        print 'total targets acq: {}, krowns per target: {}'.format(tGsum, float(baseKrowns)/(tGsum))
        print ''
    avgnchestsHist.append(trialAvgChests)
print '\noverall avg chests opened:', float(sum(avgnchestsHist)) / len(avgnchestsHist)
atHsum = 0
for x in xrange(len(targetsHists)):
    avgTarg = float(sum(targetsHists[x])) / len(targetsHists[x])
    print 'average target #{}s: {}, average krowns per target: {}'.format(x+1, avgTarg, float(baseKrowns)/avgTarg)
totalAvgTarg = float(sum(totalTargetsHist)) / len(totalTargetsHist)
print 'total average targets: {}, average krowns per target: {}'.format(totalAvgTarg, float(baseKrowns)/totalAvgTarg)
