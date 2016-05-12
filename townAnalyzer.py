import json
import snp2lib
from os import sep
import time
from operator import attrgetter


folder = 'townInfo'
savedTownsFileName = 'goodTowns.json'

with open(folder+sep+savedTownsFileName) as goodTownsFile:
    goodTowns = json.load(goodTownsFile)

sortedTowns = sorted(goodTowns.values(), key=lambda x: x['current']['population'], reverse=True)
print len(sortedTowns), 'towns at 200k+'
#print sortedTowns[0]['current'].keys()

instances = 0
topX = 8
print 'best {} towns by pop'.format(topX)
for townObj in sortedTowns[:topX]:
    instances += len(townObj['history'])
    town = townObj['current']
    if town['members_count'] != town['member_count']: print 'wtf'
    print '{:<15} {}k pop, {} players ({})'.format(town['name'], town['population'], town['members_count'],
                                                   bin(town['unlocked_resources'])[2:])
#print instances, 'instances of towns'
print ', '.join([x['current']['name'] + ' ' + str(x['current']['population']) + 'k' for x in sortedTowns])