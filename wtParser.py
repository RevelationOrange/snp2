import json
import snp2lib
from os import sep
import time


wtSets = []
folder = 'townInfo'
fnshell = 'wtRecs{}.txt'
nFiles = 4
inputFileNames = ['wtRecs3.txt']
iFNs = [fnshell.format(x) for x in xrange(nFiles)]
print iFNs
sdd = snp2lib.getSDdict()
items = sdd['items']
assets = sdd['assets']

itemName = "Soldier's Sword"
theItem = snp2lib.findByName(itemName, items, assets)
itemID = theItem['id']

for fn in iFNs:
    with open(folder+sep+fn) as inputFile:
        for line in inputFile:
            derp = json.loads(line)
            wtSets.append(derp)

''' displays all entries
for x in wtSets:
    xdate = time.ctime(x['fD'])
    for y in x['offers']:
        iName = assets[str(items[str(y['iid'])]['name_id'])]['value']
        rStr = '{}{:5} at {:>13,} gold  {}'.format('%-29s', y['ct'], y['pr'], xdate)
        prStr = rStr % iName
        print prStr
'''

for x in wtSets:
    xdate = time.ctime(x['fD'])
    for y in x['offers']:
        if y['iid'] == itemID:
            iName = itemName
            rStr = '{}{:5} at {:>13,} gold  {}'.format('%-29s', y['ct'], y['pr'], xdate)
            prStr = rStr % iName
            print prStr

# 15:55:42
# 16:15:02
