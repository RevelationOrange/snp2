import json
from copy import deepcopy
import snp2lib
import math
from os import sep
import codecs
from pprint import pprint


'''
basically a sandbox for playing with the static dump
'''

def ktt(key, thing):
    return '{}: {} ({})'.format(key, thing[key], type(thing[key]))

spacer = '  '
def outputInfo(theThing, theFile, ntabs=0):
    if type(theThing) is dict:
        for key in theThing:
            theFile.write(spacer*ntabs + '{}: '.format(key))
            if type(theThing[key]) is list:
                theFile.write('\n')
            outputInfo(theThing[key], theFile, ntabs+1)
    elif type(theThing) is list:
        for i in xrange(len(theThing)):
            theFile.write(spacer*ntabs + 'index {}:\n'.format(str(i)))
            outputInfo(theThing[i], theFile, ntabs+1)
    else:
        theFile.write(str(theThing) + '\n')
    return

def findAthing(theDict, target, keysTrail, trackList):
    if type(theDict) is dict:
        for key in theDict.keys():
            keysTrail.append(key)
            findAthing(theDict[key], target, keysTrail, trackList)
            del keysTrail[-1]
    elif type(theDict) is list:
        i=0
        for thing in theDict:
            keysTrail.append(i)
            findAthing(thing, target, keysTrail, trackList)
            del keysTrail[-1]
            i += 1
    else:
        if type(theDict) is str or type(theDict) is unicode:
            if str(target) in theDict:
                trackList.append(deepcopy(keysTrail))
                #print theDict
        else:
            if theDict == target:
                #print keysTrail
                #print keysTrail[-1], theDict
                trackList.append(deepcopy(keysTrail))
    return

def changeAthing(theDict):
    if type(theDict) is dict:
        for key in theDict.keys():
            changeAthing(theDict[key])
    elif type(theDict) is list:
        if len(theDict) > 1:
            del theDict[0]
    return

oldFileName = 'sd17238.json'
newFileName = 'sd17874.json'

with codecs.open(newFileName, 'r', 'utf-8') as sdFile:
    Dump = json.load(sdFile)
newSD = Dump

with codecs.open(oldFileName, 'r', 'utf-8') as sdFile:
    Dump = json.load(sdFile)
oldSD = Dump

'''
{u'index': 46, u'children_ids': [313], u'resource': None, u'uid': u'8c650033e57318529c93245a7631986a', u'level': 1,
u'description_id': 0, u'image': u'46_582x724_mur_top', u'parents_ids': [], u'__type__': u'Improvement',
u'build_time': 86400, u'building_modifier': u'', u'requirements': [], u'flags': 2, u'x': 582, u'y': 724,
u'name_id': 27690, u'codename': u'northwall', u'id': 312, u'modifier_unlock': u''}
'''

tracker = []
targ = 'apocaplypticstaff'
#trail = []
findAthing(newSD, targ, ['result'], tracker)

'''
with open('huntsInfo.txt', 'w') as huntsFile:
    huntsFile.write('all hunts from static dump\n\n')
    outputInfo(newSD['result']['hunts'], huntsFile)
'''

name0 = 'genesis codex'
name1 = 'lucky amulet'
for x in newSD['result']['assets_with_context']:
    if x['__type__'] != 'Improvement':
        pass
    '''
    idNum = x['name_id']
    for y in newSD['result']['assets']:
        if y['id'] == idNum:
            theName = y['value'].lower()
            if theName == name0 or theName == name1:
                print '{}: purchase: {}, repair: {}, unlock: {}, level: {}'.format(y['value'], x['purchase_cost'], x['repair_cost'], x['unlock_cost'], x['level'])
    ''' '''
    a = snp2lib.getInfo(['hunts', 'add', x], newSD['result'])
    if a is not None:
        for b in a[1]:
            print b + ': ' + str(a[1][b])
        print ''
    else:
        print a
    '''
for x in tracker:
    print x

goldTotal = 0
chkSection = 'recipe_unlocks'
testGetInfo = 1
uqIDs = []
colorAvg = []
testPrint = 1
#'''
for chkSection in sections:
    if testPrint: theFile = codecs.open('allInfo'+sep+chkSection+'.txt', 'w', 'utf-8')
    if type(newSD['result'][chkSection]) in [list, dict]:
        if chkSection == 'fame_levels':
            do = [ y for y in newSD['result'][chkSection] ]
            if testGetInfo: a = snp2lib.getInfo([chkSection, 'check', do], newSD)
            if testPrint: snp2lib.prInfo([chkSection, 'test', a[1]], theFile)
        else:
            #print chkSection
            for x in newSD['result'][chkSection]:
                #colorAvg.append(x['color'])
                #if x['id'] not in uqIDs: uqIDs.append(x['id'])
                #print x
                    #for item in newSD['result']['items']:
                    #    if item['id'] == x['crafted_item_id']: nameID = item['name_id']
                    #for asset in newSD['result']['assets']:
                    #    if asset['id'] == nameID: print asset['value'], x['worker_codename']
                if testGetInfo:
                    #for j in x:
                    #    print "%s: %s" % (j, x[j])
                    #print x
                    a = snp2lib.getInfo([chkSection, 'check', x], newSD)
                    #print a[0]
                    #for k in a[1]:
                    #    pass
                        #derp = '{!r}'.format(unicode(a[1][k]))
                        #print derp.encode('utf8')
                        #print '{}: {}'.format(k, derp)
                        #if k == 'name': nlens = max(len(a[1][k]), nlens)
                        #if k == 'reward': rlens = max(len('{} {}'.format(*a[1][k])), rlens)
                        #print "%s: %s" % (k, a[1][k])
                        #print k + ': ' + unicode(a[1][k])
                    if testPrint and chkSection in checkList: snp2lib.prInfo([chkSection, 'test', a[1]], theFile)
                    #print ''
    if testPrint: theFile.close()
#'''
#print nlens, rlens
# event quests, workers, achievements, special items
assetSearch = 0
if assetSearch:
    for x in tracker:
        if x[2] == 'assets':
            print newSD['result']['assets'][x[3]]

goldTotal = 0
itemsTotal = {}
custsTotal = {}
itemValues = 0
totalSeconds = 0
shopGold = 0
shopTime = 0
buildingCodenameDictOfNames = {}
for x in newSD['result']['improvements']:
    totalSeconds += x['build_time']
    bName = assetsDict[x['name_id']]['value']
    if bName == 'Mysterious Pillars': print bName, x['level'], x['build_time']/86400.
    if x['codename'] in buildingCodenameDictOfNames:
        buildingCodenameDictOfNames[x['codename']]['time'] += x['build_time']
    else:
        buildingCodenameDictOfNames[x['codename']] = {'name':bName, 'time':x['build_time']}
    for y in x['requirements']:
        if y['character_codename'] is not None:
            if y['character_codename'] in custsTotal:
                custsTotal[y['character_codename']] += y['amount']
            else:
                custsTotal[y['character_codename']] = y['amount']
        elif y['item_id'] != 0:
            iNameID = itemsDict[y['item_id']]['name_id']
            itemValues += itemsDict[y['item_id']]['price']*y['amount']
            iName = assetsDict[iNameID]['value']
            if iName in itemsTotal:
                itemsTotal[iName] += y['amount']
            else:
                itemsTotal[iName] = y['amount']
        else:
            goldTotal += y['amount']

for x in newSD['result']['modules']:
    if x['costs'] is not None:
        for y in x['costs']:
            if y != -1: shopGold += y*x['maximum']
    if x['build_times'] is not None:
        shopTime += sum(x['build_times'])

for x in newSD['result']['achievements']:
    aName = assetsDict[x['name_id']]['value']
    if 'Employer' in aName: print 'derpderp', x
    if x['rewards'][0]['data'] == 'skillburr': print 'derpderp', assetsDict[x['name_id']]['value'], x
    if x['rewards'][0]['type'] == 2:
        print x['rewards'][0]['data']

iids = []
nameMatches = ['sky partisan', 'apocalyptic staff']
for x in newSD['result']['items']:
    name = assetsDict[x['name_id']]['value']
    for y in nameMatches:
        if assetsDict[x['name_id']]['value'].lower() == y:
            iids.append([y, x['id']])

'''
print ''
print (goldTotal-500000000)/1e9
print ''
for x in itemsTotal:
    print '{}: {}'.format(x, itemsTotal[x])
print ''
for x in custsTotal:
    print '{}: {}'.format(x, custsTotal[x])
print ''
print (itemValues)
print ''
print totalSeconds/86400./365.2425, 'days'
print ''
print 'total shop gold: {}\ntotal shop time: {} years'.format(shopGold, shopTime/86400./365.2425)
print ''
with open('buildLineTimes.txt', 'w') as buildtxtfile:
    for x in buildingCodenameDictOfNames:
        buildtxtfile.write('{}: {} days\n'.format(buildingCodenameDictOfNames[x]['name'], buildingCodenameDictOfNames[x]['time']/86400.))
'''
print ''
for x in iids:
    print '{}: {}'.format(*x)
