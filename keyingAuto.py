import snp2lib
from os import sep
import codecs
import json


def getRareCount(rec, qty, pre=0):
    rares = []
    for ingr in rec['components']:
        iid = ingr['item_id']
        if iid != 0:
            if items[str(iid)]['type'] == rareTypeNum: rares.append([iid, ingr['quantity']*qty])
            #elif not pre: rares += getRareCount(recipes[str(iid)], ingr['quantity']*qty, 1)
    return rares

raresFolder = 'raresKeys' + sep
rareratesFilename = raresFolder + 'rareRates.txt'
keyingInfoFilename = raresFolder + 'keyingInfo.csv'
checkedRecsFilename = raresFolder + 'checkedRecs.csv'
startPacketFilename = raresFolder + 'startPacket.txt'
rareTypeNum = snp2lib.rareTypeNum
sdDict = snp2lib.getSDdict()
recipes = sdDict['recipes']
items = sdDict['items']
recUnlocks = sdDict['recipe_unlocks']
assets = sdDict['assets']

with open('sd17874.json') as sdRegularFile: sdReg = json.load(sdRegularFile)

with open(startPacketFilename) as startPacketFile:
    for line in startPacketFile: startPacketText = line
startPacket = json.loads(startPacketText)
playerInvy = startPacket['result']['player']['item_instances']
playerRecipes = startPacket['result']['player']['recipe_instances']
unlockedIDs = [x['recipe_id'] for x in playerRecipes]

print 'setting up rareData'
rareData = {}
for id in sdDict['items']:
    if sdDict['items'][id]['type'] == rareTypeNum:
        rareData[id] = {'name':sdDict['assets'][str(sdDict['items'][id]['name_id'])]['value'], 'remaining':0}

print 'reading in rare rates info'
rareratesText = []
with open(rareratesFilename) as rrFile:
    for line in rrFile: rareratesText.append(line.split('\n')[0].split(','))

print 'adding rare rates to rareData'
for rareStats in rareratesText:
    for id in rareData:
        if rareData[id]['name'].lower() == rareStats[0]:
            rareData[id]['raresPerHour'] = rareStats[4]
            rareData[id]['estValue'] = rareStats[5]

print 'getting non unlocked recipes'
nonUnlockedRecs = []
for iid in items:
    item = items[iid]
    if int(iid) not in unlockedIDs and item['level']:
        for ruid in recUnlocks:
            recu = recUnlocks[ruid]
            if recu['recipe_id'] == int(iid): nonUnlockedRecs.append(recu)

print 'getting rare items remaining'
rareItemsRemaining = []
for x in nonUnlockedRecs:
    if x['crafted_item_count']:
        rID = x['crafted_item_id']
        name = assets[str(items[str(rID)]['name_id'])]['value']
        crftd = 0
        for y in playerInvy:
            if y['item_id'] == rID: crftd = y['crafted']
        qty = x['crafted_item_count'] - crftd
        unlockID = x['recipe_id']
        recRares = getRareCount(recipes[str(rID)], qty)
        if len(recRares) > 0:
            FI = snp2lib.getInfo(['fullItems', 'getInfo', rID], sdReg)[1]
            rareItemsRemaining.append([assets[str(items[str(rID)]['name_id'])]['value'],
                                       assets[str(items[str(unlockID)]['name_id'])]['value'], FI['madeOn'],
                                       FI['madeBy'], qty, items[str(unlockID)]['level'], recRares])
            for x in recRares: rareData[str(x[0])]['remaining'] += x[1]

print 'getting rares on hand'
for x in playerInvy:
    iid = str(x['item_id'])
    if snp2lib.isRareID(iid):
        rareData[iid]['onHand'] = x['count']
        rareData[iid]['needed'] = rareData[iid]['remaining'] - rareData[iid]['onHand']

print 'making keying info'
keyingInfo = {}
for item in rareItemsRemaining:
    while item[0] in keyingInfo: item[0] += ' '
    keyingInfo[item[0]] = {'time':0, 'value':0, 'tpk':0, 'vpk':0, 'unlocks':item[1], 'keys':item[-2], 'rares':''}
    keyingInfo[item[0]]['rares'] = ','.join([ '{},{}'.format(rareData[str(x[0])]['name'], x[1]) for x in item[-1] ])
    for rare in item[-1]:
        keyingInfo[item[0]]['time'] += rare[1]/float(rareData[str(rare[0])]['raresPerHour'])
        keyingInfo[item[0]]['value'] += rare[1]*float(rareData[str(rare[0])]['estValue'])
    keyingInfo[item[0]]['value'] /= 1e6
    keyingInfo[item[0]]['vpk'] = (keyingInfo[item[0]]['value']/item[-2])
    keyingInfo[item[0]]['tpk'] = keyingInfo[item[0]]['time']/item[-2]
    keyingInfo[item[0]]['station'] = '{} {}'.format(*item[2])
    keyingInfo[item[0]]['worker'] = item[3]
    keyingInfo[item[0]]['remaining'] = item[4]

headers = ['skipped item', 'left to make', 'value per key (M)', 'time per key (h)',
           'keys needed', 'unlocked item', 'total value (M)', 'total time',
           'station', 'worker', 'rares involved']
prStr = ','.join(headers) + '\n'

sKeyingInfo = sorted(keyingInfo, key=lambda x: keyingInfo[x]['vpk'], reverse=True)
for rare in sKeyingInfo:
    addStr = '{},{remaining},{vpk},{tpk},{keys},%s,{value},{time},{station},{worker},{rares}\n' % keyingInfo[rare]['unlocks']
    prStr += addStr.format(rare, **keyingInfo[rare])
prStr += '\n,total remaining,have,,needed\n'

for id in rareData:
    if rareData[id]['remaining'] > 0: prStr += '{name},{remaining},{onHand},,{needed}\n'.format(**rareData[id])

print prStr
with codecs.open(keyingInfoFilename, 'w', 'utf-8') as keyingInfoFile: keyingInfoFile.write(prStr)
