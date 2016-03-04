import json
from copy import deepcopy
import snp2lib


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

with open(newFileName, 'r') as sdFile:
    Dump = json.load(sdFile)
newSD = Dump

with open(oldFileName, 'r') as sdFile:
    Dump = json.load(sdFile)
oldSD = Dump

'''
{u'index': 46, u'children_ids': [313], u'resource': None, u'uid': u'8c650033e57318529c93245a7631986a', u'level': 1,
u'description_id': 0, u'image': u'46_582x724_mur_top', u'parents_ids': [], u'__type__': u'Improvement',
u'build_time': 86400, u'building_modifier': u'', u'requirements': [], u'flags': 2, u'x': 582, u'y': 724,
u'name_id': 27690, u'codename': u'northwall', u'id': 312, u'modifier_unlock': u''}
'''

tracker = []
targ = 392
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
chkSection = 'krown_rewards'
testGetInfo = 0
uqIDs = []
#'''
for x in newSD['result'][chkSection]:
    #print x
    #if x['id'] not in uqIDs: uqIDs.append(x['id'])
    #print x
        #for item in newSD['result']['items']:
        #    if item['id'] == x['crafted_item_id']: nameID = item['name_id']
        #for asset in newSD['result']['assets']:
        #    if asset['id'] == nameID: print asset['value'], x['worker_codename']
    if testGetInfo:
        a = snp2lib.getInfo([chkSection, 'check', x], newSD)
        print a[0]
        for k in a[1]:
            print k + ':', a[1][k]
        print ''
#'''
# event quests, workers, achievements, special items
assetSearch = 0
if assetSearch:
    for x in tracker:
        if x[2] == 'assets':
            print newSD['result']['assets'][x[3]]

#for x in newSD['result']['assets']:
#    if x['id'] == 25544: print x

# ['result', u'result', u'recipes', 210, u'id']
# ['result', u'result', u'items', 210, u'id']
# ['result', u'result', u'recipe_unlocks', 210, u'id']
dictA = {'a':0, 'c':0}
dictB = {'b':'c', 'c':'a'}
dictD = {1:1, 2:0}
derp = [['recipes', newSD['result']['recipes'][391]], ['items', newSD['result']['items'][391]], ['recipe_unlocks', newSD['result']['recipe_unlocks'][358]], ['recipe_unlocks', newSD['result']['recipe_unlocks'][358+1]]]
derpList = []
for x in derp:
    y = snp2lib.getInfo([x[0], 'test', x[1]], newSD)
    derpList.append(y[1])
testDerp = {}
for x in derpList:
    testDerp.update(x)
for x in derpList:
    print x
for x in testDerp:
    print x + ':', testDerp[x]
print len(testDerp), 7+9+2+2
#dictC = dict(dictB, **dictA)
#dictA.update(dictB)
#print dictA
snp2lib.printInfo(['customers'])