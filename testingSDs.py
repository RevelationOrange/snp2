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
            keysTrail.append('[list ' + str(i) + ']')
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

oldFileName = 'sd17873.json'
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
targ = 'derp'
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
chkSection = 'modules'
testGetInfo = 0
for x in newSD['result'][chkSection]:
    #if 'iron_mine' in x['codename']: print x['modifier_unlock']
    if 'table' in x['codename']:
        print x['codename'], x['power']
        for y in x['modifiers']:
            print y
        print ''
    if testGetInfo:
        a = snp2lib.getInfo([chkSection, 'check', x], newSD)
        print a[0]
        for k in a[1]:
            print k + ':', a[1][k]
        print ''
    '''
        if 'add' in x['modifier_unlock']['modifier']:
            if x['modifier_unlock']['modifier']['add'] == 0: print x['modifier_unlock']['modifier']['add'], x['modifier_unlock']
        #print 'id {}: children {}, {} ({})'.format(x['id'], x['children_ids'], str(childBuildings)[1:-1], x['parents_ids'])
    if len(x['requirements']) > 0:
        if type(x['requirements'][0]['character_codename']) is type(None) and x['requirements'][0]['item_id'] == 0:
            goldTotal += x['requirements'][0]['amount']
#print newSD['result']['appeal_levels']
print goldTotal/1e9
'''