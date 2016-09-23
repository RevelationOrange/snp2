import snp2lib
from os import sep
import codecs
import json


def getRareCount(rec, qty, pre=0):
    # count up the rares in a recipe
    rares = []
    for ingr in rec['components']:
        iid = ingr['item_id']
        if iid != 0:
            if items[str(iid)]['type'] == rareTypeNum: rares.append([iid, ingr['quantity']*qty])
            #elif not pre: rares += getRareCount(recipes[str(iid)], ingr['quantity']*qty, 1)
    return rares

# these are the folders/files required for this to run
# raresFolder is where everything goes, rareRates.txt is an input file, as is startPacket.txt
# keyingInfo.csv is the outputm checkedRecs is old and not used
raresFolder = 'raresKeys' + sep
rareratesFilename = raresFolder + 'rareRates.txt'
keyingInfoFilename = raresFolder + 'keyingInfo.csv'
checkedRecsFilename = raresFolder + 'checkedRecs.csv'
startPacketFilename = raresFolder + 'startPacket.txt'
rareTypeNum = snp2lib.rareTypeNum
sdDict = snp2lib.getSDdict()
# recipes, recipe unlocks, and items dict, by id (as a string)
recipes = sdDict['recipes']
items = sdDict['items']
recUnlocks = sdDict['recipe_unlocks']
assets = sdDict['assets']

# I think I could have done snp2lib.getPlainSD() here, but I forget
with open('sd17874.json') as sdRegularFile: sdReg = json.load(sdRegularFile)

# this grabs the start packet, what the server sends you when you first load
with open(startPacketFilename) as startPacketFile:
    for line in startPacketFile: startPacketText = line
startPacket = json.loads(startPacketText)
# from the start packet, get the player inventory and recipes
playerInvy = startPacket['result']['player']['item_instances']
playerRecipes = startPacket['result']['player']['recipe_instances']
# make a list of the uloocked ids
unlockedIDs = [x['recipe_id'] for x in playerRecipes]

print 'setting up rareData'
rareData = {}
for id in sdDict['items']:
    if sdDict['items'][id]['type'] == rareTypeNum:
        # for each item, if it's a rare resource, add its name and remaining=0 to the rareData dict
        # remaining is how many left you need for crafting
        rareData[id] = {'name':sdDict['assets'][str(sdDict['items'][id]['name_id'])]['value'], 'remaining':0}

print 'reading in rare rates info'
rareratesText = []
with open(rareratesFilename) as rrFile:
    # this file contains the value for each rare, and how many rares you get per hour when focused on farming them
    for line in rrFile: rareratesText.append(line.split('\n')[0].split(','))

print 'adding rare rates to rareData'
for rareStats in rareratesText:
    for id in rareData:
        if rareData[id]['name'].lower() == rareStats[0]:
            # the text file contains rare data as:
            # name, rare/hr when farming with 1 dungeon, 2 dungeons, 3, 4, value, and I can't remember what the last number is but it's not used anyway
            rareData[id]['raresPerHour'] = rareStats[4]
            rareData[id]['estValue'] = rareStats[5]

print 'getting non unlocked recipes'
nonUnlockedRecs = []
for iid in items:
    item = items[iid]
    if int(iid) not in unlockedIDs and item['level']:
        # check each item id, if it's not in the unlocked list:
        for ruid in recUnlocks:
            # go through the recipe unlocks, find the item that unlocks it, and add it to the nonunlocked list
            recu = recUnlocks[ruid]
            if recu['recipe_id'] == int(iid): nonUnlockedRecs.append(recu)

print 'getting rare items remaining'
rareItemsRemaining = []
for x in nonUnlockedRecs:
    if x['crafted_item_count']:
        # go through the nonunlocked recipes, if crafted_item_count is nonzero:
        rID = x['crafted_item_id']
        name = assets[str(items[str(rID)]['name_id'])]['value']
        crftd = 0
        # check how many have been crafted so far
        for y in playerInvy:
            if y['item_id'] == rID: crftd = y['crafted']
        qty = x['crafted_item_count'] - crftd
        # qty is how many you have left to craft
        unlockID = x['recipe_id']
        # get the rares involved in the recipe
        recRares = getRareCount(recipes[str(rID)], qty)
        if len(recRares) > 0:
            # if there are any, add to the rare items remaining list:
            # [name of the item, name of the item it unlocks, workstation, crafter, level, rare ids]
            FI = snp2lib.getInfo(['fullItems', 'getInfo', rID], sdReg)[1]
            rareItemsRemaining.append([assets[str(items[str(rID)]['name_id'])]['value'],
                                       assets[str(items[str(unlockID)]['name_id'])]['value'], FI['madeOn'],
                                       FI['madeBy'], qty, items[str(unlockID)]['level'], recRares])
            # add the rares involved to the remaining rares needed
            for x in recRares: rareData[str(x[0])]['remaining'] += x[1]

print 'getting rares on hand'
for x in playerInvy:
    iid = str(x['item_id'])
    if snp2lib.isRareID(iid):
        # go through the player inventory and add up the rares they have on hand
        rareData[iid]['onHand'] = x['count']
        rareData[iid]['needed'] = rareData[iid]['remaining'] - rareData[iid]['onHand']

print 'making keying info'
keyingInfo = {}
for item in rareItemsRemaining:
    # this is just a thing to avoid similar names I think, I forget exactly
    while item[0] in keyingInfo: item[0] += ' '
    # make a base dict for the total time, total value, time per key, value per key, what it unlocks, number of keys, and rares involved
    # the rest of this is just populating those values
    keyingInfo[item[0]] = {'time':0, 'value':0, 'tpk':0, 'vpk':0, 'unlocks':item[1], 'keys':item[-2], 'rares':''}
    keyingInfo[item[0]]['rares'] = ','.join([ '{},{}'.format(rareData[str(x[0])]['name'], x[1]) for x in item[-1] ])
    for rare in item[-1]:
        # add up time and value, using the rares per hour and estValue from the rareData
        keyingInfo[item[0]]['time'] += rare[1]/float(rareData[str(rare[0])]['raresPerHour'])
        keyingInfo[item[0]]['value'] += rare[1]*float(rareData[str(rare[0])]['estValue'])
    # this is so the prices are displayed in millions
    keyingInfo[item[0]]['value'] /= 1e6
    keyingInfo[item[0]]['vpk'] = (keyingInfo[item[0]]['value']/item[-2])
    keyingInfo[item[0]]['tpk'] = keyingInfo[item[0]]['time']/item[-2]
    keyingInfo[item[0]]['station'] = '{} {}'.format(*item[2])
    keyingInfo[item[0]]['worker'] = item[3]
    keyingInfo[item[0]]['remaining'] = item[4]

# at this point, it's just formatting output
headers = ['skipped item', 'left to make', 'value per key (M)', 'time per key (h)',
           'keys needed', 'unlocked item', 'total value (M)', 'total time',
           'station', 'worker', 'rares involved']
prStr = ','.join(headers) + '\n'

# this sorts by value per key, once it's in a csv, it's easy to sort by whatever other header in excel
sKeyingInfo = sorted(keyingInfo, key=lambda x: keyingInfo[x]['vpk'], reverse=True)
for rare in sKeyingInfo:
    addStr = '{},{remaining},{vpk},{tpk},{keys},%s,{value},{time},{station},{worker},{rares}\n' % keyingInfo[rare]['unlocks']
    prStr += addStr.format(rare, **keyingInfo[rare])
prStr += '\n,total remaining,have,,needed\n'

for id in rareData:
    if rareData[id]['remaining'] > 0: prStr += '{name},{remaining},{onHand},,{needed}\n'.format(**rareData[id])

print prStr
with codecs.open(keyingInfoFilename, 'w', 'utf-8') as keyingInfoFile: keyingInfoFile.write(prStr)
