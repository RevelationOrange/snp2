import json
import snp2lib
from os import sep
import time


townSets = []
folder = 'townInfo'
inputFileNames = ['townsearch.txt', 'townsearch0.txt', 'townsearch1.txt', 'townsearch2.txt', 'townsearch3.txt',
                  'townsearch4.txt', 'townsearch5.txt', 'townsearch6.txt', 'townsearch7.txt']
savedTownsFileName = 'goodTowns.json'
structureFileName = 'struct.txt'

for inputFileName in inputFileNames:
    with open(folder+sep+inputFileName) as inputFile:
        for line in inputFile:
            #print type(line)
            derp = json.loads(line)
            townSets.append(derp)

with open(folder+sep+savedTownsFileName) as savedTownsFile:
    a = json.load(savedTownsFile)

goodTowns = a
warTowns = []
names = []
stLenGood = len(goodTowns)
updates = 0
earliestTime = 1459905321.44
for x in townSets:
    if 'fetchDate' not in x: theTime = earliestTime
    else: theTime = x['fetchDate']
    #print len(x['result']['groups'])
    for y in x['result']['groups']:
        y['fetchDate'] = theTime
        names.append(y['name'])
        if y['members_count'] != y['member_count']: print 'wtf'
        if y['population'] > 199:
            if y['name'] in goodTowns:
                curTown = goodTowns[y['name']]['current']
                if y['fetchDate'] > curTown['fetchDate']:
                    if y['population'] != curTown['population'] or y['member_count'] != curTown['member_count']:
                        updates += 1
                        goodTowns[y['name']]['history'].append(y)
                        goodTowns[y['name']]['current'] = y
            else:
                goodTowns[y['name']] = {'current': y, 'history':[y]}
        if y['war_points'] != 0 or y['tournament_war_points'] != 0: warTowns.append(y)

endLenGood = len(goodTowns)
print '{} good towns added, {} good towns updated'.format(endLenGood-stLenGood, updates)
if len(warTowns) > 0:
    print '\nwar towns:'
    for x in warTowns:
        print '{:<15} war wins/losses/points/tourney points: {:<} {:<} {:<} {:<} '.format(x['name'], x['war_wins'],
                                                                                          x['war_losses'],
                                                                                          x['war_points'],
                                                                                          x['tournament_war_points'])

with open(folder+sep+savedTownsFileName, 'w') as savedTownsFile:
    json.dump(goodTowns, savedTownsFile)

print '{} entries, {} unique towns'.format(len(names), len(set(names)))
print '\n',time.time()
