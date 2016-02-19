import json
from copy import deepcopy


'''
basically a sandbox for playing with the static dump
'''

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

oldFileName = 'tmp0.json'
newFileName = 'tmp.json'

with open(newFileName, 'r') as sdFile:
    Dump = json.load(sdFile)
newSD = Dump

with open(oldFileName, 'r') as sdFile:
    Dump = json.load(sdFile)
oldSD = Dump

#items = newSD['items']
#for x in items[-3:]:
#    print x

#print len(items)
#items[470]['price'] = 21000
#print items[470]
#print len(items)

'''
{u'index': 46, u'children_ids': [313], u'resource': None, u'uid': u'8c650033e57318529c93245a7631986a', u'level': 1,
u'description_id': 0, u'image': u'46_582x724_mur_top', u'parents_ids': [], u'__type__': u'Improvement',
u'build_time': 86400, u'building_modifier': u'', u'requirements': [], u'flags': 2, u'x': 582, u'y': 724,
u'name_id': 27690, u'codename': u'northwall', u'id': 312, u'modifier_unlock': u''}
'''

#print sd['CUSTOMER_AFFINITY']

tracker = []
targ = 2500
#trail = []
findAthing(newSD, targ, ['result'], tracker)

for x in tracker:
    print x

#for cust in newSD['customers']:
#    if cust['id'] == 25:
#        pass

#for x in tracker:
#    print x
n=-5
for x in [343+n, 351+n, 359+n]:
    building = newSD['result']['improvements'][x]
    print building['codename'], building['level'], building['modifier_unlock']['modifier']['add']
