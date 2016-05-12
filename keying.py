import snp2lib
from os import sep
import codecs
from copy import deepcopy
import json


def getRareCount(rec, qty, pre=0):
    rares = []
    for ingr in rec['components']:
        iid = ingr['item_id']
        if iid != 0:
            if items[str(iid)]['type'] == rareTypeNum: rares.append([iid, ingr['quantity']*qty])
            #elif not pre: rares += getRareCount(recipes[str(iid)], ingr['quantity']*qty, 1)
    return rares

raresFolder = 'raresKeys'
rareratesFilename = raresFolder + sep + 'rareRates.txt'
keyingInfoFilename = raresFolder + sep + 'keyingInfo.csv'
checkedRecsFilename = raresFolder + sep + 'checkedRecs.csv'
rareTypeNum = snp2lib.rareTypeNum
sdDict = snp2lib.getSDdict()
recipes = sdDict['recipes']
items = sdDict['items']
recUnlocks = sdDict['recipe_unlocks']
assets = sdDict['assets']

with open('sd17874.json') as sdRegularFile: sdReg = json.load(sdRegularFile)

rareData = {}
for id in sdDict['items']:
    if sdDict['items'][id]['type'] == rareTypeNum:
        rareData[id] = {'name':sdDict['assets'][str(sdDict['items'][id]['name_id'])]['value'], 'remaining':0}

checkedRecs = {}
with open(checkedRecsFilename) as chkRecsFile:
    for line in chkRecsFile:
        lineList = line.split('\n')[0].split(',')
        checkedRecs[lineList[0]] = lineList[1]

rareratesText = []
with open(rareratesFilename) as rrFile:
    for line in rrFile: rareratesText.append(line.split('\n')[0].split(','))

for rareStats in rareratesText:
    for id in rareData:
        if rareData[id]['name'].lower() == rareStats[0]:
            rareData[id]['raresPerHour'] = rareStats[4]
            rareData[id]['estValue'] = rareStats[5]

rareItems = []
for id in recUnlocks:
    if recUnlocks[id]['crafted_item_count']:
        rID = recUnlocks[id]['crafted_item_id']
        name = assets[str(items[str(rID)]['name_id'])]['value']
        if name in checkedRecs:
            if int(checkedRecs[name]):
                qty = recUnlocks[id]['crafted_item_count']
                unlockID = recUnlocks[id]['recipe_id']
                recRares = getRareCount(recipes[str(rID)], qty)
                if len(recRares) > 0:
                    FI = snp2lib.getInfo(['fullItems', 'getInfo', rID], sdReg)[1]
                    rareItems.append([assets[str(items[str(rID)]['name_id'])]['value'],
                                      assets[str(items[str(unlockID)]['name_id'])]['value'], FI['madeOn'], FI['madeBy'],
                                      items[str(unlockID)]['level'], recRares])
                    for x in recRares: rareData[str(x[0])]['remaining'] += x[1]

keyingInfo = {}
for item in rareItems:
    print item
    while item[0] in keyingInfo: item[0] += ' '
    keyingInfo[item[0]] = {'time':0, 'value':0, 'tpk':0, 'vpk':0, 'unlocks':item[1], 'keys':item[-2], 'rares':''}
    keyingInfo[item[0]]['rares'] = ', '.join([ '{} x{}'.format(rareData[str(x[0])]['name'], x[1]) for x in item[-1] ])
    for rare in item[-1]:
        keyingInfo[item[0]]['time'] += rare[1]/float(rareData[str(rare[0])]['raresPerHour'])
        keyingInfo[item[0]]['value'] += rare[1]*float(rareData[str(rare[0])]['estValue'])
    keyingInfo[item[0]]['vpk'] = (keyingInfo[item[0]]['value']/item[-2])/1e6
    keyingInfo[item[0]]['tpk'] = keyingInfo[item[0]]['time']/item[-2]
    keyingInfo[item[0]]['station'] = '{} {}'.format(*item[2])
    keyingInfo[item[0]]['worker'] = item[3]
    print '{:24} {}'.format(item[0], keyingInfo[item[0]])

print len(rareItems)
print rareData
headers = ['skipped item', 'value per key (M)', 'time per key (h)',
           'keys needed', 'unlocked item', 'total value', 'total time', 'station', 'worker', 'rares involved']
prStr = ','.join(headers) + '\n'

for rare in keyingInfo:
    addStr = '{},{vpk},{tpk},{keys},%s,{value},{time},{station},{worker},{rares}\n' % keyingInfo[rare]['unlocks']
    prStr += addStr.format(rare, **keyingInfo[rare])
prStr += '\n'

for id in rareData:
    if rareData[id]['remaining'] > 0: prStr += '{name},{remaining}\n'.format(**rareData[id])

print prStr
with codecs.open(keyingInfoFilename, 'w', 'utf-8') as keyingInfoFile: keyingInfoFile.write(prStr)
