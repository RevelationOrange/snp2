from itertools import compress
from copy import deepcopy
import json


'''
snp2lib will hold any function that might be useful later on (not just for dealing with the static dump)
for now, it's mainly for getInfo, which will deal with customers, city improvements, etc. found in a difference check
'''

# this is the base url for getting images and such from edgebee
# along with a type version because it's easier
cdnBase = "cdn.edgebee.com/static/"
cndBase = cdnBase

ctimeConverter = {0:'none', 1:'Very Short', 2:'Short', 3:'Medium', 4:'Long',  5:'Very Long'}
ctimeFloatConverter = {0:0.0, 1:0.2, 2:0.3, 3:0.4, 4:0.7,  5:1.0}
sddFilename = 'sdDict.json'
sdpFilename = 'sd17921.json'
rareTypeNum = 536870912

# I found this solution on stack exchange, to pass a mask as an argument to a list to select which entries to return
class maskList(list):
    def __getitem__(self, index):
        try: return super(maskList, self).__getitem__(index)
        except TypeError: return maskList(compress(self, index))

spacer = '  '
def traverseDict(theDict, theFile, ntabs=0):
    # traverseDict will determine and output the full structure of a json object
    if type(theDict) is dict:
        # if it's a dict, go through each key, record it in theFile, and pass the next thing down
        for key in theDict:
            theFile.write(spacer*ntabs + key + '\n')
            traverseDict(theDict[key], theFile, ntabs+1)
    elif type(theDict) is list:
        # if it's a list, record that it's a list
        theFile.write(spacer*ntabs + 'list of stuff with keys:' + '\n')
        if len(theDict) > 0:
            # if there's stuff in the list, pass each thing down
            traverseDict(theDict[0], theFile, ntabs+1)
    else:
        # record the type of variable it finds
        theFile.write(spacer*ntabs + str(type(theDict)) + '\n')
    return

def makeSDdict(curSD):
    if 'result' in curSD: curSD = curSD['result']
    extractList = prInfo()
    extractList.remove('fullItems')
    extractList.append('resources')
    SDdict = {}
    for key in extractList:
        SDdict[key] = {}
        if type(curSD[key][0]) is dict:
            print key, 'check'
            for thing in curSD[key]:
                #print thing
                SDdict[key][thing['id']] = thing
                #print key, thing['id'], thing
    with open('sdDict.json', 'w') as sdDictFile:
        json.dump(SDdict, sdDictFile)

'''
def makeNiceSDdict(curSD):
    if 'result' in curSD: curSD = curSD['result']
    extractList = prInfo()
    extractList.remove('fullItems')
    SDdict = {}
    for key in extractList:
        SDdict[key] = {}
    return
'''

def getSDdict():
    with open(sddFilename) as sddFile:
        sd = json.load(sddFile)
    return sd

def getPlainSD():
    with open(sdpFilename) as sdPlainFile:
        sd = json.load(sdPlainFile)
    return sd

def findByName(name, theDict, assets):
    for id in theDict:
        if assets[str(theDict[id]['name_id'])]['value'].lower() == name.lower(): return theDict[id]

def findAssetRefs(theDict, target, keysTrail, trackList):
    if type(theDict) is dict:
        for key in theDict.keys():
            keysTrail.append(key)
            findAssetRefs(theDict[key], target, keysTrail, trackList)
            del keysTrail[-1]
    elif type(theDict) is list:
        i=0
        for thing in theDict:
            keysTrail.append(i)
            findAssetRefs(thing, target, keysTrail, trackList)
            del keysTrail[-1]
            i += 1
    else:
        if type(theDict) is str or type(theDict) is unicode:
            if str(target) in theDict:
                trackList.append(deepcopy(keysTrail))
        else:
            if theDict == target:
                trackList.append(deepcopy(keysTrail))
    return

def getCats(iMask):
    # item types are stored in a bit of a strange way: as a bitmask corresponding to the category list:
    catList = maskList( ['swords', 'axes', 'maces', 'spears', 'daggers', 'staves', 'bows', 'music', 'thrown', 'guns',
                         'heavy armor', 'armor', 'clothes', 'heavy helmets', 'helmets', 'hats', 'gauntlets', 'gloves',
                         'bracers', 'heavy boots', 'boots', 'shoes', 'shields', '', 'potions', 'herbs', 'scrolls',
                         'rings', 'amulets', 'rare resources'] )
    # the items_mask value must be converted to a binary number, which, when using bin(), actually makes it a string for
    # some reason, with '0b' at the beginning, so we use element 2 to the end to only get the actual number
    # then, we need to reverse the number; as stored, the 2^0 bit corresponds to swords, so we want that to always
    # be the first digit
    # then just convert each thing to int (since at that point they're all still characters), and save it to mask
    mask = [ int(y) for y in reversed([x for x in bin(iMask)][2:]) ]
    # apply the mask to the category list and return it
    return catList[mask]

def prCustomer(modType, cust, theFile):
    if modType == 'change':
        if cust['newname'] == cust['oldname']: prStr = '{newname} ({newclass})\n'
        else: prStr = 'New: {newname} ({newclass})\nOld: {oldname} ({oldclass})\n'
        textKeys = [['Start level', 'newstartLvl', 'oldstartLvl'],
                    ['Max level', 'newmaxLvl', 'oldmaxLvl'],
                    ['Fame required', 'newlvlReq', 'oldlvlReq'],
                    ['Appeal required', 'newappealReq', 'oldappealReq'],
                    #['Unlocked by', '--', '--'],
                    ['Color', 'newcolor', 'oldcolor']]
        if len(cust['newunlockedBy']) > 0: newUnlock = '{newunlockedBy[0]} {newunlockedBy[1]}'.format(**cust)
        else: newUnlock = '--'
        if len(cust['oldunlockedBy']) > 0: oldUnlock = '{oldunlockedBy[0]} {oldunlockedBy[1]}'.format(**cust)
        else: oldUnlock = '--'
        replStr = '{:<17}{:<20}{:<}\n'
        header = replStr.format('', 'New', 'Old')
        prStr += header
        for x in textKeys: prStr += replStr.format(x[0], cust[x[1]], cust[x[2]])
        prStr += replStr.format('Unlocked by', newUnlock, oldUnlock)
        if cust['newiTypes'] == cust['oldiTypes']: prStr += 'Favorite items: {}\n'.format(', '.join(cust['newiTypes']))
        else: prStr += 'New favorite items: {}\nOld favorite items: {}\n'.format(', '.join(cust['newiTypes']),
                                                                                 ', '.join(cust['oldiTypes']))
        prStr += '(id:{newid})\n\n'
        theFile.write(prStr.format(**cust))
    else:
        theFile.write('{} ({})\n'.format(cust['name'], cust['class']))
        theFile.write('Level range: ' + str(cust['startLvl']) + '-' + str(cust['maxLvl']) + '\n')
        theFile.write('Favorite item types: ' + ', '.join(cust['iTypes']) + '\n')
        theFile.write('Fame required: ' + str(cust['lvlReq']) + '\nAppeal required: ' + str(cust['appealReq']) + '\n')
        theFile.write('Unlocked by: ')
        if len(cust['unlockedBy']) > 0:
            theFile.write(' '.join(str(x) for x in cust['unlockedBy']))
        else:
            theFile.write('--')
        theFile.write('\nColor: {} (id:{})\n\n'.format(cust['color'], cust['id']))

def prHunt(modType, hunt, theFile):
    if modType == 'change':
        textKeys = [['Name', '{newname}', '{oldname}'],
                    ['Level range', '{newminLvl}-{newmaxLvl}', '{oldminLvl}-{oldmaxLvl}'],
                    ['Duration', '', ''],
                    ['Level required', '{newshopLvlReq}', 'oldshopLvlReq'],
                    ['Common loot', '{newloots[0][0]} {newloots[0][1]}', '{oldloots[0][0]} {oldloots[0][1]}'],
                    ['Uncommon loot', '{newloots[1][0]} {newloots[1][1]}', '{oldloots[1][0]} {oldloots[1][1]}'],
                    ['Rare loot', '{newloots[2][0]} {newloots[2][1]}', '{oldloots[2][0]} {oldloots[2][1]}'],
                    ['XP per loot', '{newxpPerLoot}', '{oldxpPerLoot}'],
                    ['100% common', '{newcomValue}', '{oldcomValue}']]
        if hunt['newtime'] < 1: newTime = '{} minutes'.format(hunt['newtime']*60)
        elif hunt['newtime'] == 1: newTime = '{newtime} hour'
        else: newTime = '{newtime} hours'
        if hunt['oldtime'] < 1: oldTime = '{} minutes'.format(hunt['oldtime']*60)
        elif hunt['oldtime'] == 1: oldTime = '{oldtime} hour'
        else: oldTime = '{oldtime} hours'
        textKeys[2][1] = newTime
        textKeys[2][2] = oldTime
        replStr = '{:<16}{:<16}{:<}\n'
        header = replStr.format('', 'New', 'Old')
        prStr = header
        for x in textKeys: prStr += replStr.format(*x)
        prStr += 'New description: {newdescription}\nOld description: {olddescription}\nNew icon: {newpicLink}\n'
        prStr += 'Old icon: {oldpicLink}\n(id:{newid})\n\n'
        theFile.write(prStr.format(**hunt))
    else:
        theFile.write('{}\n{}\n'.format(hunt['name'], hunt['description']))
        theFile.write('Level range: {}-{}\n'.format(str(hunt['minLvl']), str(hunt['maxLvl'])))
        if hunt['time'] < 1: time = str(int(hunt['time']*60)) + ' minutes'
        elif hunt['time'] == 1: time = str(int(hunt['time'])) + ' hour'
        else: time = str(int(hunt['time'])) + ' hours'
        theFile.write('Duration: {}\nLevel required: {}\n'.format(time, hunt['shopLvlReq']))
        theFile.write('Common/Uncommon/Rare loots: {}\n'.format( ' / '.join( [' '.join( str(x) for x in y) for y in
                                                                              hunt['loots']] ) ))
        theFile.write('XP per loot: {:,}\nValue for 100% common: {:,} gold\n'.format(hunt['xpPerLoot'],
                                                                                     hunt['comValue']))
        theFile.write('Icon link: {} (id:{})\n\n'.format(hunt['picLink'], hunt['id']))

def prImprovement(modType, impr, theFile):
    if modType == 'change':
        replStr = 'New: {newname} level {newlevel}\nOld: {oldname} level {oldlevel}\nNew description: {newdescription}'
        replStr += '\nOld description: {olddescription}\n'
        if len(impr['newupgradeCost']) > 0: replStr += 'New unlock cost: {newupgradeCost[0]:,} {newupgradeCost[1]}\n'
        else: replStr += '(starter building)'
        if len(impr['oldupgradeCost']) > 0: replStr += 'Old unlock cost: {oldupgradeCost[0]:,} {oldupgradeCost[1]}\n'
        else: replStr += '(starter building)'
        replStr += 'New upgrade duration: {newtime} hours\nOld upgrade duration: {oldtime} hours\nNew unlocked by: '
        if type(impr['newunlockedBy']) is list: replStr += '{newunlockedBy[0]} level {newunlockedBy[1]}'
        else: replStr += '{newunlockedBy}'
        replStr += '\nOld unlocked by: '
        if type(impr['oldunlockedBy']) is list: replStr += '{oldunlockedBy[0]} level {oldunlockedBy[1]}\n'
        else: replStr += '{oldunlockedBy}\n'
        if impr['newbuildUnlocks'] != 'none' and len(impr['newbuildUnlocks']) > 0:
            replStr += 'New buildings unlocked: {}\n'.format(', '.join([x[0] for x in impr['newbuildUnlocks']]))
        if impr['oldbuildUnlocks'] != 'none' and len(impr['oldbuildUnlocks']) > 0:
            replStr += 'Old buildings unlocked: {}\n'.format(', '.join([x[0] for x in impr['oldbuildUnlocks']]))
        if impr['newbonus'] != 'none': replStr += 'New bonus: {newbonus[0]} +{newbonus[1]}\n'
        if impr['oldbonus'] != 'none': replStr += 'New bonus: {oldbonus[0]} +{oldbonus[1]}\n'
        if impr['newcustUnlocks'] != 'none':
            replStr += 'New customers unlocked: {}\n'.format(', '.join(['{} ({})'.format(*x) for x in
                                                                        impr['newcustUnlocks']]))
        if impr['oldcustUnlocks'] != 'none':
            replStr += 'Old customers unlocked: {}\n'.format(', '.join(['{} ({})'.format(*x) for x in
                                                                        impr['oldcustUnlocks']]))
        replStr += 'New image: {newpicLink}\nOld image: {oldpicLink}\n(id:{newid})\n\n'
        prStr = replStr.format(**impr)
        theFile.write(prStr)
    else:
        theFile.write('{}, level {}\n{}\n'.format(impr['name'], impr['level'], impr['description']))
        theFile.write('Cost to unlock this level: ')
        if len(impr['upgradeCost']) > 0:
            theFile.write('{:,} {}'.format(*impr['upgradeCost']))
        else:
            theFile.write('starter building')
        theFile.write('\nUpgrade duration: {} hours\nUnlocked by: '.format(impr['time']))
        if type(impr['unlockedBy']) is list:
            theFile.write('{} level {}\n'.format(*impr['unlockedBy']))
        else:
            theFile.write(impr['unlockedBy'] + '\n')
        if impr['buildUnlocks'] != 'none':
            if len(impr['buildUnlocks']) > 0:
                theFile.write('Buildings unlocked: {}\n'.format(', '.join([x[0] for x in impr['buildUnlocks']])))
        if impr['bonus'] != 'none': theFile.write('Bonus: {} +{}\n'.format(*impr['bonus']))
        if impr['custUnlocks'] != 'none':
            theFile.write('Customers unlocked: {}\n'.format(', '.join(['{} ({})'.format(*x) for x in
                                                                       impr['custUnlocks']])))
        theFile.write('Image link: {} (id:{})\n\n'.format(impr['picLink'], str(impr['id'])))


def prFameLevel(modType, fameLevel, theFile):
    # for this, I want to have it take all the new fame levels at once and write them; one entry per level would be weird
    # so that's the plan once I come back to this
    pass

def prCustLevelValue(modType, cust, theFile):
    pass

def prRecUnlock(modType, recUnlock, theFile):
    if modType == 'change':
        replStr = 'New: to unlock {newitemUnlocked}, craft {newitemToCraft[1]} {newitemToCraft[0]}\n'
        replStr += 'Old: to unlock {olditemUnlocked}, craft {olditemToCraft[1]} {olditemToCraft[0]}\n(id:{newid})\n\n'
        theFile.write(replStr.format(**recUnlock))
    else:
        if recUnlock['itemUnlocked'] != '':
            theFile.write('To unlock %s, craft %d %s\n(id:%d)\n\n' %
            (recUnlock['itemUnlocked'], recUnlock['itemToCraft'][1], recUnlock['itemToCraft'][0], recUnlock['id']) )

def prAsset(modType, asset, theFile):
    if modType == 'change':
        replStr = 'New text: {newtext}\nOld text: {oldtext}\nNew locations in SD:\n'
        for loc in asset['newlocationsUsed']:
            replStr += '[' + ']['.join([ str(x) for x in loc ]) + ']\n'
        replStr += 'Old locations in SD:\n'
        for loc in asset['oldlocationsUsed']:
            replStr += '[' + ']['.join([ str(x) for x in loc ]) + ']\n'
        replStr += '(id:{newid})\n\n'
        prStr = replStr.format(**asset)
        theFile.write(prStr)
    else:
        theFile.write("Text: %s\nLocations referencing this text in the static dump:\n" % (asset['text']))
        for place in asset['locationsUsed']:
            theFile.write('[' + ']['.join([ str(x) for x in place ]) + ']\n')
        theFile.write("(id:%d)\n\n" % asset['id'])

def prItem(modType, item, theFile):
    if modType == 'change':
        textKeys = [['Level', 'newlevel', 'oldlevel'],
                    ['Category', 'newtype', 'oldtype'],
                    ['Price', 'newvalue', 'oldvalue'],
                    ['Craft XP', 'newcraftXP', 'oldcraftXP'],
                    ['Sell XP', 'newsellXP', 'oldsellXP'],
                    ['Coupon repair cost', 'newrepairCost', 'oldrepairCost']]
        nameLength = len(item['newname']) + 2
        replStr = '{:<20}{:<%d}{:<}\n' % nameLength
        header = replStr.format('', 'New', 'Old')
        prStr = header
        prStr += 'Name                %s  %s\n' % (item['newname'], item['oldname'])
        for x in textKeys:
            prStr += replStr.format(x[0], item[x[1]], item[x[2]])
        prStr += 'New image: {newpicLink}\nOld image: {oldpicLink}\n(id:{newid})\n\n'.format(**item)
        theFile.write(prStr)
    else:
        theFile.write("%s, level %d\nCategory: %s\nPrice: %d\nCraft xp: %d\nSell xp: %d\n" %
        (item['name'], item['level'], item['type'], item['value'], item['craftXP'], item['sellXP']) )
        theFile.write("Coupon cost to buy back: %d\nImage link: %s (id:%d)\n\n" %
                      (item['repairCost'], item['picLink'], item['id']) )

def prRecipe(modType, rec, theFile):
    if modType == 'change':
        textKeys = [['Name', 'newname', 'oldname'],
                    ['Category', 'newtype', 'oldtype'],
                    ['Worker', 'newmadeBy', 'oldmadeBy'],
                    ['Craft speed', 'newcraftTime', 'oldcraftTime']]
        nameLength = max(len(rec['newname']), len(rec['newmadeBy'])) + 2
        replStr = '{:<13}{:<%d}{:<}\n' % nameLength
        header = replStr.format('', 'New', 'Old')
        prStr = header
        for x in textKeys:
            prStr += replStr.format(x[0], rec[x[1]], rec[x[2]])
        replStr = 'New station: {0}\nOld station: {1}\nNew craft speed:{newcraftTime}\nOld craft speed:{oldcraftTime}\n'
        replStr += 'New ingredients:\n\t{2}\nOld ingredients:\n\t{3}\n(id:{newid})\n\n'
        newIngrs = '\n\t'.join('x '.join([str(x[0]), x[1]]) for x in rec['newingredients']) if\
            type(rec['newingredients']) is list else 'none'
        oldIngrs = '\n\t'.join('x '.join([str(x[0]), x[1]]) for x in rec['oldingredients']) if\
            type(rec['oldingredients']) is list else 'none'
        prStr += replStr.format(' level '.join(str(x) for x in rec['newmadeOn']),
                                ' level '.join(str(x) for x in rec['oldmadeOn']), newIngrs, oldIngrs, **rec)
        theFile.write(prStr)
    else:
        ingrs = '\n\t'.join('x '.join([str(x[0]), x[1]]) for x in rec['ingredients']) if type(rec['ingredients']) is\
                                                                                         list else 'none'
        replStr = '%s\nCategory: {type}\nWorker: {madeBy}\nStation: {0}\nCraft speed: {craftTime}\n' % rec['name']
        replStr += 'Ingredients:\n\t{1}\n(id:{id})\n\n'
        prStr = replStr.format(' level '.join(str(x) for x in rec['madeOn']), ingrs, **rec)
        theFile.write(prStr)

def prModule(modType, module, theFile):
    if modType == 'change':
        textKeys = [['Name', 'newname', 'oldname'],
                    ['Tier', 'newtier', 'oldtier'],
                    ['Level unlocked', 'newlevelReq', 'oldlevelReq'],
                    ['Max w/gold', 'newmaxBuyable', 'oldmaxBuyable'],
                    ['Hammer cost', 'newhammerCost', 'oldhammerCost'],
                    ['Unlocked by', 'newunlockedBy', 'oldunlockedBy']]
        nameLength = len(module['newname']) + 2
        replStr = '{:<16}{:<%d}{:<}\n' % nameLength
        header = replStr.format('', 'New', 'Old')
        prStr = header
        for x in textKeys:
            prStr += replStr.format(x[0], module[x[1]], module[x[2]])
        newSpacerList = ["{:<8}{:<9}", "{:<10}"]
        oldSpacerList = ["{:<8}{:<9}", "{:<10}"]
        newHeaders = ['Level', 'Gold cost', 'Build time']
        oldHeaders = ['Level', 'Gold cost', 'Build time']
        newAppeals = False
        oldAppeals = False
        newBonuses = 0
        oldBonuses = 0
        if module['newappeals'] is not None:
            newAppeals = True
            newSpacerList.append("{:<6}")
            newHeaders.append('Appeal')
        if module['oldappeals'] is not None:
            oldAppeals = True
            oldSpacerList.append("{:<6}")
            oldHeaders.append('Appeal')
        for newBonus in module['newbonuses']:
            newBonuses += 1
            if len(module['newbonuses']) == newBonuses: newSpacerList.append("{:<}")
            else: newSpacerList.append("{:<" + str(len(newBonus[0])) + "}")
            newHeaders.append(newBonus[0])
        for oldBonus in module['oldbonuses']:
            oldBonuses += 1
            if len(module['oldbonuses']) == oldBonuses: oldSpacerList.append("{:<}")
            else: oldSpacerList.append("{:<" + str(len(oldBonus[0])) + "}")
            oldHeaders.append(oldBonus[0])
        newSpacerLine = '\t'.join(newSpacerList)
        oldSpacerLine = '\t'.join(oldSpacerList)
        prStr += 'New stats\n'
        prStr += newSpacerLine.format(*newHeaders) + '\n'
        newSpacerList[0] = "{:<8}{:<9,}"
        newSpacerLine = '\t'.join(newSpacerList)
        if module['newtimes'] is not None:
            for i in xrange(len(module['newtimes'])):
                if module['newtimes'][i] < 3600: newTime = '{}m'.format(module['newtimes'][i]/60)
                elif module['newtimes'][i] < 86400: newTime = '{}h'.format(module['newtimes'][i]/3600)
                else: newTime = '{}d'.format(module['newtimes'][i]/86400)
                newLine = [i+1, module['newgoldCosts'][i], newTime]
                if newAppeals: newLine.append(module['newappeals'][i])
                if newBonuses: newLine += [x[1][i] for x in module['newbonuses']]
                prStr += newSpacerLine.format(*newLine) + '\n'
        prStr += 'Old stats\n'
        prStr += oldSpacerLine.format(*oldHeaders) + '\n'
        oldSpacerList[0] = "{:<8}{:<9,}"
        oldSpacerLine = '\t'.join(oldSpacerList)
        if module['oldtimes'] is not None:
            for i in xrange(len(module['oldtimes'])):
                if module['oldtimes'][i] < 3600: oldTime = '{}m'.format(module['oldtimes'][i]/60)
                elif module['oldtimes'][i] < 86400: oldTime = '{}h'.format(module['oldtimes'][i]/3600)
                else: oldTime = '{}d'.format(module['oldtimes'][i]/86400)
                oldLine = [i+1, module['oldgoldCosts'][i], oldTime]
                if oldAppeals: oldLine.append(module['oldappeals'][i])
                if oldBonuses: oldLine += [x[1][i] for x in module['oldbonuses']]
                prStr += oldSpacerLine.format(*oldLine) + '\n'
        prStr += 'New image: {newpicLink}\nOld image: {oldpicLink}\n(id:{newid})\n\n'.format(**module)
        theFile.write(prStr)
    else:
        unlck = module['unlockedBy'] if module['unlockedBy'] == 'none' else module['unlockedBy']
        theFile.write("%s, tier %d\nUnlocked at level %d\nMax buyable with gold: %d\nHammer cost per level: %d\n" %
        (module['name'], module['tier'], module['levelReq'], module['maxBuyable'], module['hammerCost']) )
        theFile.write("Unlocked by: %s\nImage link: %s\n" % (unlck, module['picLink']) )
        spacerList = ["{:<8}{:<9}", "{:<10}"]
        headers = ['Level', 'Gold cost', 'Build time']
        appeals = False
        if module['appeals'] is not None:
            appeals = True
            spacerList.append("{:<6}")
            headers.append('Appeal')
        bonuses = 0
        for bonus in module['bonuses']:
            bonuses += 1
            if len(module['bonuses']) == bonuses:
                spacerList.append("{:<}")
            else:
                spacerList.append("{:<" + str(len(bonus[0])) + "}")
            headers.append(bonus[0])
        spacerLine = '\t'.join(spacerList)
        theFile.write(spacerLine.format(*headers) + '\n')
        spacerList[0] = "{:<8}{:<9,}"
        spacerLine = '\t'.join(spacerList)
        if module['times'] is not None:
            for i in xrange(len(module['times'])):
                if module['times'][i] < 3600: time = '{}m'.format(module['times'][i]/60)
                elif module['times'][i] < 86400: time = '{}h'.format(module['times'][i]/3600)
                else: time = '{}d'.format(module['times'][i]/86400)
                line = [i+1, module['goldCosts'][i], time]
                if appeals: line.append(module['appeals'][i])
                if bonuses: line += [x[1][i] for x in module['bonuses']]
                theFile.write(spacerLine.format(*line) + '\n')
        theFile.write('(id:{})\n\n'.format(module['id']))

def prQuest(modType, quest, theFile):
    if modType == 'change':
        textKeys = [['Name', 'newname', 'oldname'], ['Level unlocked', 'newshopLevelReq', 'oldshopLevelReq'],
                    ['Duration', 'newtime', 'oldtime'], ['XP per customer', 'newxp', 'oldxp'],
                    ['Reward', 'newreward', 'oldreward'], ['Previous quest', 'newunlockedBy', 'oldunlockedBy']]
        replStr = '{:<16}{:<24}{:<}\n'
        header = replStr.format('', 'new', 'old')
        prStr = header
        for x in textKeys:
            prStr += replStr.format(x[0], quest[x[1]], quest[x[2]])
        replStr = 'New intro text: {newintroText}\nOld intro text: {oldintroText}\nNew outro text: {newoutroText}\n'
        replStr += 'Old outro text: {oldoutroText}\nNew customers to send: {0}\n Old customers to send: {1}\n'
        replStr += 'New items needed: {2}\nOld items needed: {3}\nNew icon link: {newpicLink}\n'
        replStr += 'Old icon link: {oldpicLink}\n(id:{newid})\n\n'
        prStr += replStr.format(', '.join(quest['newcustsNeeded']), ', '.join(quest['oldcustsNeeded']),
                                ', '.join(quest['newitemsNeeded']), ', '.join(quest['olditemsNeeded']), **quest)
        theFile.write(prStr)
    else:
        theFile.write('{name}\nIntro text: "{introText}"\nOutro test: "{outroText}"\n'.format(**quest) )
        theFile.write('Unlocked at level: {shopLevelReq}\nDuration: {time} hrs\nXP per customer: {xp}\n'.format(**quest))
        theFile.write('Reward: {}\nPrevious quest in line: {unlockedBy}\n'.format('{} {}'.format(*quest['reward']),**quest))
        theFile.write('Customers to send: {}\nItems needed: {}\n'.format(', '.join(quest['custsNeeded']),
                                                                         ', '.join(quest['itemsNeeded'])) )
        theFile.write('Icon link: {picLink} (id:{id})\n\n'.format(**quest))

def prWorker(modType, worker, theFile):
    if modType == 'change':
        textKeys = [['Name', 'newname', 'oldname'], ['Level unlocked', 'newshopLevelReq', 'oldshopLevelReq'],
                    ['Gold to hire', 'newgoldCost', 'oldgoldCost'], ['Coupons to hire', 'newcouponCost',
                                                                     'oldcouponCost']]
        replStr = '{:18}{:<7}{:<}\n'
        header = replStr.format('', 'new', 'old')
        prStr = ''
        for x in textKeys:
            prStr += replStr.format(x[0], worker[x[1]], worker[x[2]])
        theFile.write(header + prStr + '\n')
    else:
        theFile.write('{name}\nUnlocked at level {shopLevelReq}\n'.format(**worker))
        theFile.write('Cost to hire:\n{goldCost:,} gold or {couponCost} coupons\n(id:{id})\n\n'.format(**worker))

def prAchievement(modType, achievement, theFile):
    theFile.write('{name}\n{requirement}\n'.format(**achievement))
    if type(achievement['reward']) is list: rew = ' '.join(achievement['reward'])
    else: rew = achievement['reward']
    theFile.write('Reward: {}\n\n'.format(rew))

def prCharClass(modType, cclass, theFile):
    if modType == 'change':
        replString = 'Name'
        if cclass['newname'] == cclass['oldname']: replString += ': {newname}\n'
        else: replString += ' new/old:\t{newname}\t{oldname}\n'
        if cclass['newdescription'] == cclass['olddescription']: replString += 'Description: {newdescription}\n'
        else: replString += 'New description: {newdescription}\nOld description: {olddescription}\n'
        if cclass['newklashItems'] == cclass['oldklashItems']: replString += 'Klash items: {newklashItems}\n'
        else: replString += 'New klash items: {newklashItems}\nOld klash items: {oldklashItems}\n'
        if cclass['newicon'] == cclass['oldicon']: replString += 'Icon link: {newicon}\n'
        else: replString += 'New icon: {newicon}\nOld icon: {oldicon}\n'
        if cclass['newfullPic'] == cclass['oldfullPic']: replString += 'Full image: {newfullPic}\n'
        else: replString += 'New full image: {newfullPic}\nOld full image: {oldfullPic}\n'
        replString += '(id:{newid})\n\n'
        theFile.write(replString.format(**cclass))
    else:
        replString = ''
        if cclass['name'] == 'none': replString += '(npc)\n'
        else: replString += '{name}\n'
        if cclass['description'] != 'none': replString += 'Description: {description}\n'
        if type(cclass['klashItems']) is not maskList: replString += '{klashItems}'
        else: replString += 'Equipable in klash: {}'.format(', '.join(cclass['klashItems']))
        replString += '\nIcon link: {icon}\nFull image: {fullPic} (id:{id})\n\n'
        prString = replString.format(**cclass)
        theFile.write(prString)

def prFameLevel(modType, fameLevels, theFile):
    prStr = 'Level\tXP from previous level\n'
    prStr += '\n'.join(['{:<5}\t{:,}'.format(*x) for x in fameLevels])
    theFile.write(prStr + '\n\n')

def prCustLevelValue(modType, cust, theFile):
    if modType == 'change':
        theFile.write('{:<7}{:<11}{}'.format('Level','new value','old value'))
        theFile.write('{:<7}{:,<11}{:,}'.format(cust['newLevel'], cust['newvalue'], cust['oldvalue']))
    else:
        theFile.write('Level: {level}, value: {value:,}\n\n'.format(**cust))

def prFullItem(modType, fullItem, theFile):
    textKeys = [['Worker', '{madeBy}'],
                ['Workstation', '{madeOn[0]} {madeOn[1]}'],
                ['Sell Price', '{value:,}'],
                ['Crafting XP', '{craftXP:,}'],
                ['Selling XP', '{sellXP:,}'],
                ['Ingredients', '{ingrs}'],
                ['Crafting Speed', '{craftTime}'],
                ['Category', '{type}'],
                ['Unlocks', '{unlck}'],
                ['Unlocked by', '{unlckBy}'],
                ['Needed for recipes', '{recipes}'],
                ['Needed for quests', '{quests}'],
                ['Needed for buildings', '{buildings}'],
                ['Picture link', '{picLink}']]
    spacerStr = '{:<22}{:<}\n'
    replStr = '\t\t%s (Level {level})\n' % fullItem['name']
    for x in textKeys: replStr += spacerStr.format(*x)
    replStr += '(id:{id})\n\n'
    indentedSpacer = '\n' + ' '*22
    if fullItem['ingredients'] == 'none': ingrs = '--'
    else: ingrs = indentedSpacer.join([ '%dx %s' % (x[0], x[1]) for x in fullItem['ingredients'] ])
    if fullItem['nextItem'] == '--': unlck = '--'
    else: unlck = '%s (%dx)' % (fullItem['nextItem'][0], fullItem['nextItem'][1])
    if type(fullItem['prevItem']) is unicode or type(fullItem['prevItem']) is str: unlckBy = fullItem['prevItem']
    elif fullItem['prevItem'] == []: unlckBy = '(starter recipe)'
    else: unlckBy = '%s (%sx)' % (fullItem['prevItem'][0], fullItem['prevItem'][1])
    #if fullItem['nsfRecs'][0] == '--': recipes = '--'
    recipes = ', '.join(fullItem['nfRecs'])
    quests = ', '.join(fullItem['nfQuests'])
    if fullItem['nfBuilds'][0] == '--': buildings = '--'
    else: buildings = indentedSpacer.join([ '{} {} ({}x)'.format(*x) for x in fullItem['nfBuilds'] ])
    prStr = replStr.format(ingrs=ingrs, unlck=unlck, unlckBy=unlckBy, recipes=recipes, quests=quests,
                           buildings=buildings, **fullItem)
    theFile.write(prStr)

def prInfo(printObj=0, outpFile=0):
    printInfoDict = {'customers':prCustomer, 'hunts':prHunt, 'improvements':prImprovement, 'fame_levels':prFameLevel,
                     'customer_level_values':prCustLevelValue, 'recipe_unlocks':prRecUnlock, 'assets':prAsset,
                     'items':prItem, 'recipes':prRecipe, 'modules':prModule, 'quests':prQuest, 'workers':prWorker,
                     'achievements':prAchievement, 'character_classes':prCharClass, 'fullItems':prFullItem}
    if printObj == 0: return printInfoDict.keys()

    prType = printObj[0]
    if prType != 'fullItems': outpFile.write('{}\n'.format(printObj[1]))
    printInfoDict[prType](printObj[1], printObj[2], outpFile)

def getInfo(change=0, newSD=0):
    # getInfo is the master function to determine the type of change in the static dump and all the info about it
    # currently works for: customers (sans color), quests
    # maybe change it later so each case is a separate function and store them in a dict? who knows

    # default return when given no arguments is a list of change types accepted
    if change == 0:
        return ['customers', 'hunts', 'improvements', 'fame_levels', 'customer_level_values', 'recipe_unlocks',
                'assets', 'items', 'recipes', 'modules', 'quests', 'workers', 'achievements', 'character_classes',
                'fullItems']

    # if the main dict was passed as newSD, bypass that silly 'result' key
    if 'result' in newSD:
        newSD = newSD['result']

    # putting the assets in their own place just saves typing, as nearly every section needs to search through it
    assets = newSD['assets']

    # get the type of change
    changeType = change[0]
    if changeType == 'customers':
        ''' example customer:
        {u'character_class_id': 35, u'uid': u'5ac120fe88819387bfbab3b1840d2611', u'min_fame': 65,
        u'simple_class': u'knight', u'max_level': 20, u'__type__': u'Customer', u'color': 2236962, u'min_appeal': 10,
        u'starting_level': 15, u'name_id': 27710, u'improvement_id': 52, u'id': 161, u'items_mask': 4268040}
        '''
        # change[2] stores the actual changed object
        newCust = change[2]
        # set up the output customer, get the data that's immediately available: start and max level, level requirement
        # to unlock, and appeal requirement to unlock (and color, which is a hex code stored in dec)
        outputCust = {'name':'', 'startLvl':newCust['starting_level'], 'maxLvl':newCust['max_level'],
                      'class':'', 'lvlReq':newCust['min_fame'], 'appealReq':newCust['min_appeal'],
                      'iTypes':[], 'unlockedBy':[], 'color':hex(newCust['color']), 'id':newCust['id']}
        # the IDs here are used to get the respective names
        classID = newCust['character_class_id']
        nameID = newCust['name_id']
        imprID = newCust['improvement_id']
        # imask is a bitmask that determines a customer's buy list when applied to catList
        iMask = newCust['items_mask']
        # go through the character classes and improvements to get the name ids for the class of and improvement to
        # unlock the customer, plus the level of the improvement
        for cclass in newSD['character_classes']:
            if cclass['id'] == classID:
                classNameID = cclass['name_id']
        for impr in newSD['improvements']:
            if impr['id'] == imprID:
                imprNameID = impr['name_id']
                imprLevel = impr['level']
        # then go through the assets, which is apparently where all text is stored (there's probly a good reason, I
        # dunno) and find each id, getting the 'value' of its asset object (where the text is stored) and storing it
        for asset in assets:
            chkID = asset['id']
            if chkID == imprNameID:
                imprName = asset['value']
            elif chkID == nameID:
                outputCust['name'] = asset['value']
            elif chkID == classNameID:
                className = asset['value']
        # update the output customer
        outputCust['unlockedBy'] = [imprName, imprLevel]
        outputCust['class'] = className
        outputCust['iTypes'] = getCats(iMask)
        # return change[1] (whether it's an add, removal, or change) and the new customer
        return [change[1], outputCust]

    elif changeType == 'hunts':
        ''' example quest:
        {u'min_level': 20, u'min_value': 200000, u'unlock_fame_level': 90, u'__type__': u'Hunt', u'max_level': 21,
        u'max_value': 4000000.0, u'image': u'shopr2/quests/dungeon_27.png', u'rewards_mask': 0, u'loots': [{u'index': 0,
        u'resource_id': 0, u'__type__': u'HuntLoot', u'value': 0, u'amount': 1, u'item_id': 563, u'id': 82},
        {u'index': 1, u'resource_id': 0, u'__type__': u'HuntLoot', u'value': 0, u'amount': 2, u'item_id': 563,
        u'id': 83}, {u'index': 2, u'resource_id': 0, u'__type__': u'HuntLoot', u'value': 0, u'amount': 3,
        u'item_id': 563, u'id': 84}], u'npc': u'npc_ranger', u'description_id': 27732, u'name_id': 27731,
        u'quest_id': 0, u'customer_xp_reward': 7467, u'duration': 230400, u'improvement_id': 0, u'id': 28}
        '''
        # grab the new quest
        newHunt = change[2]
        # fill out the easy stuff: min and max level, time (convert to hours), level required, xp/loot, value for 100%
        # common reward (which for some reason is stored in min_value and needs to be doubled, or max_value divided by
        # 10), a link to the quest icon, and empty loot entries, stored as [amount, item/resource/'gold']
        outputQuest = {'name':'', 'minLvl':newHunt['min_level'], 'maxLvl':newHunt['max_level'],
                       'time':newHunt['duration']/3600., 'shopLvlReq':newHunt['unlock_fame_level'],
                       'loots':[[0,''], [0,''], [0,'']], 'xpPerLoot':newHunt['customer_xp_reward'],
                       'comValue':newHunt['min_value']*2, 'description':'', 'picLink':cdnBase+newHunt['image'],
                       'id':newHunt['id']}
        # name and description id are simply there, grab them
        nameID = newHunt['name_id']
        descID = newHunt['description_id']
        for i in xrange(len(newHunt['loots'])):
            # while the names for the loots are a bit more complicated
            # each loot can be an item, a resource, or gold; if either of the item or resource ids of the loot are
            # non-zero, that is the type of loot it is (they can't both be non-zero), otherwise it's gold
            if newHunt['loots'][i]['item_id'] > 0:
                # if it's an item or resource, set its id to the appropriate thing from newHunt, and set the key to
                # either 'items' or 'resources'; these are to be used to find the name of the loot in the right place
                thingID = newHunt['loots'][i]['item_id']
                searchKey = 'items'
            elif newHunt['loots'][i]['resource_id'] > 0:
                thingID = newHunt['loots'][i]['resource_id']
                searchKey = 'resources'
            else:
                # if it's gold, we don't want to search the assets or anything, so just set the loot entry to [amout,
                # 'gold'] and use continue to skip the rest
                outputQuest['loots'][i][1] = "Gold"
                outputQuest['loots'][i][0] = newHunt['loots'][i]['amount']
                continue
            # if it's an item or resource, use the id to find the name id in the respective location
            for thing in newSD[searchKey]:
                if thing['id'] == thingID:
                    thingNameID = thing['name_id']
            # then find the text in assets and set the loot's name
            for asset in assets:
                if asset['id'] == thingNameID:
                    outputQuest['loots'][i][1] = asset['value']
            # finally set the loot's amount
            outputQuest['loots'][i][0] = newHunt['loots'][i]['amount']
        # now go through assets and get the text for the quest name and description
        for asset in assets:
            chkID = asset['id']
            if chkID == nameID:
                outputQuest['name'] = asset['value']
            elif chkID == descID:
                outputQuest['description'] = asset['value']
        # and return the change status and new quest
        return [change[1], outputQuest]

    elif changeType == 'improvements':
        ''' example improvement:
        {u'index': 106, u'children_ids': [358], u'resource': None, u'uid': u'9dcb759b22b211eaeafb0b7a9ae7e9cb',
        u'level': 3, u'description_id': 0, u'image': u'106_1830x138_blue_mercs', u'parents_ids': [356],
        u'__type__': u'Improvement', u'flags': 2, u'build_time': 172800, u'building_modifier': u'', u'name_id': 27730,
        u'x': 1830, u'y': 138, u'requirements': [{u'index': 0, u'customer_xp_reward': 0,
                                                 u'__type__': u'ImprovementRequirement', u'character_codename': u'bard',
                                                 u'amount': 200, u'item_id': 0, u'improvement_id': 357, u'id': 296}],
        u'codename': u'spellcasters_guild', u'id': 357,
        u'modifier_unlock': {u'min_shop_appeal': 0, u'modifier': {u'while_building': False, u'is_global': True,
        u'__type__': u'Modifier', u'add': 400.0, u'id': 431, u'iso_y': 0.0, u'iso_x': 0.0, u'radius': 0.0,
        u'hidden': False, u'overwrites': False, u'modifies': u'klash_merc_max.spellcasters', u'mult': 0.0},
        u'__type__': u'Modifier', u'id': 231}}
        '''
        # get the new improvement (heh)
        newBuilding = change[2]
        allBuildings = newSD['improvements']
        # fill out the easy stuff
        # what we want to know, probly: name, level, how to unlock, build time, customers/stuff that's unlocked,
        # previous building, type of building (maybe), description maybe? if id is nonzero
        outputBuilding = {'name':'', 'level':newBuilding['level'], 'time':newBuilding['build_time']/3600,
                          'buildUnlocks':[], 'custUnlocks':[], 'bonus':[], 'upgradeCost':[], 'description':'',
                          'unlockedBy':[], 'picLink':cdnBase+'shopr2/city/improvements/'+newBuilding['image']+'.png',
                          'id':newBuilding['id']}
        # get the easy test from assets
        nameID = newBuilding['name_id']
        descID = newBuilding['description_id']
        for asset in assets:
            if asset['id'] == nameID: outputBuilding['name'] = asset['value']
            elif asset['id'] == descID: outputBuilding['description'] = asset['value']
        # first, find the building that unlocks this one, if it exists
        if len(newBuilding['parents_ids']) > 0:
            for impr in allBuildings:
                if impr['id'] == newBuilding['parents_ids'][0]:
                    for asset in assets:
                        if asset['id'] == impr['name_id']: outputBuilding['unlockedBy'] = [asset['value'],
                                                                                           impr['level']]
        else: outputBuilding['unlockedBy'] = 'initially available or unlocked by VP'
        # get the requirements, if they exist
        if len(newBuilding['requirements']) > 0:
            # put the dict in reqDict, makes things easier
            reqDict = newBuilding['requirements'][0]
            # get the amount, easy
            amt = reqDict['amount']
            # then there are 3 cases for the type of thing, an item, a customer, or gold
            # only one of item_id and character_codename can be nonzero or non-None, respectively
            if reqDict['item_id'] != 0:
                # if item_id is nonzero, the type of thing is an item; get the name id, then the name from assets
                for item in newSD['items']:
                    if item['id'] == reqDict['item_id']: iNameID = item['name_id']
                for asset in assets:
                    if asset['id'] == iNameID: thing = asset['value']
            elif reqDict['character_codename'] is None: thing = 'gold'
            # if item_id is 0 and character_codename is None, amt is the amount of gold
            # admittedly the order of the logic is odd here, but I just prefer to do 'is None' rather than 'is not None'
            else: thing = reqDict['character_codename']
            # otherwise character_codename isn't blank, and amt is the amount of a type of customer to send
            # put the amount and the thing into the upgrade_cost list
            outputBuilding['upgradeCost'] = [amt, thing]
        # get the building unlocks, if there are any
        if len(newBuilding['children_ids']) > 0:
            for cid in newBuilding['children_ids']:
                for impr in allBuildings:
                    if impr['id'] == cid and newBuilding['codename'] != impr['codename']:
                        for asset in assets:
                            if asset['id'] == impr['name_id']: imprName = asset['value']
                        outputBuilding['buildUnlocks'].append([imprName, impr['level']])
        else: outputBuilding['buildUnlocks'] = 'none'
        # get customer unlocks, if any
        # this requires going through the customers section, since no building actually stores info about a customer it
        # unlocks
        custUnlcks = []
        # go through every customer
        for cust in newSD['customers']:
            # if the improvement that unlocks the customer matches the id of the new building:
            if cust['improvement_id'] == newBuilding['id']:
                # get the name ids for the customer and their class (class name id is retrieved from the character
                # classes section), then go through assets to get the actual text
                custNameID = cust['name_id']
                custClassID = cust['character_class_id']
                for cclass in newSD['character_classes']:
                    if cclass['id'] == custClassID: custClassNameID = cclass['name_id']
                for asset in assets:
                    if asset['id'] == custNameID: custName = asset['value']
                    elif asset['id'] == custClassNameID: custClassName = asset['value']
                # add the name and class to the list
                custUnlcks.append([custName, custClassName])
        # if any classes were found, set the custUnlocks key to the custUnlcks list, otherwise set it to 'none'
        if len(custUnlcks) > 0: outputBuilding['custUnlocks'] = custUnlcks
        else: outputBuilding['custUnlocks'] = 'none'
        # finally, get the bonus the building provides, if any
        if type(newBuilding['modifier_unlock']) is dict:
            # the thing the building modifies will always be there, in modifier -> modifies
            what = newBuilding['modifier_unlock']['modifier']['modifies']
            # if the key 'add' is present, it contains how much of 'what' the building provides
            if 'add' in newBuilding['modifier_unlock']['modifier']:
                howMuch = newBuilding['modifier_unlock']['modifier']['add']
            # if 'add' isn't there, the how much is stored in 'mult', which is only the case for the monastery
            # so gg there edgebee, way to be consistent
            else: howMuch = newBuilding['modifier_unlock']['modifier']['mult']
            outputBuilding['bonus'] = [what, howMuch]
        # if there's no 'modifier_unlock', set the 'bonus' to 'none'
        else: outputBuilding['bonus'] = 'none'
        return [change[1], outputBuilding]

    elif changeType == 'customer_levels':
        pass
    elif changeType == 'fame_levels':
        newShopLevels = change[2]
        outputShopLevels = []
        #print newShopLevels
        for xp in newShopLevels:
            #print xp
            outputShopLevels.append([newSD[changeType].index(xp)+1, xp])
        return [change[1], outputShopLevels]

    elif changeType == 'customer_level_values':
        # very simple section, the new/old/changed level value is the number given
        newCustLevelValue = change[2]
        outputLevel = {'value':newCustLevelValue}
        # if it's an addition, the new level is the length of the list, minus 1
        if change[1] == 'add': outputLevel['level'] = len(newSD[changeType])-1
        # if it's a removal, the old level was the length of the list
        elif change[1] == 'rem': outputLevel['level'] = len(newSD[changeType])
        # if it's a change, find the index with the new value, that's the level (since it has that weird 0 at the start)
        else: outputLevel['level'] = newSD[changeType].index(newCustLevelValue)
        return [change[1], outputLevel]

    elif changeType == 'recipe_unlocks':
        ''' example recipe unlock:
        {u'worker_codename': None, u'uid': u'8ec9d260ca17c4d0ea598e5e04f69c70', u'fame_level': 0,
        u'__type__': u'RecipeUnlock', u'recipe_id': 484, u'crafted_item_id': 483, u'quest_id': 0,
        u'crafted_item_count': 48, u'module_level': 0, u'module_id': 0, u'id': 443}
        '''
        # grab the recipe unlock
        newRecUnlock = change[2]
        # fill out the easy stuff
        outputRecUnlock = {'itemToCraft':[], 'itemUnlocked':'', 'id':newRecUnlock['id'],
                           'craftID':newRecUnlock['crafted_item_id']}
        # if the item has a crafted item count of 0, it's a starting recipe or it comes with a worker
        # so for nonzero ones:
        if newRecUnlock['crafted_item_count'] != 0:
            for item in newSD['items']:
                if item['id'] == newRecUnlock['recipe_id']: iUnameID = item['name_id']
                elif item['id'] == newRecUnlock['crafted_item_id']: cInameID = item['name_id']
            for asset in assets:
                if asset['id'] == iUnameID: outputRecUnlock['itemUnlocked'] = asset['value']
                elif asset['id'] == cInameID: outputRecUnlock['itemToCraft'] = [asset['value'],
                                                                                newRecUnlock['crafted_item_count']]
        return [change[1], outputRecUnlock]

    elif changeType == 'assets':
        # assets are just text storage, and the only thing to know about them is where they're referenced
        newAsset = change[2]
        outputAsset = {'text':newAsset['value'], 'id':newAsset['id'], 'locationsUsed':[]}
        findAssetRefs(newSD, newAsset['id'], ['result'], outputAsset['locationsUsed'])
        return [change[1], outputAsset]

    elif changeType == 'items':
        ''' example item:
        {u'hue': 0, u'uid': u'cf7201e5909e9104ab35ac4ecd924e27', u'purchase_cost': 21, u'level': 21,
        u'image': u'shopr2/items/US_genesiscodex.png', u'__type__': u'Item', u'repair_cost': 5, u'id': 556,
        u'price': 2100000, u'name_id': 27720, u'craft_xp': 294002, u'type_str': u'US', u'sell_xp': 1176008,
        u'type': 67108864, u'purchase_price': 1050000, u'unlock_cost': 21}
        '''
        # grab the new item
        newItem = change[2]
        # fill out the easy stuff, all but the name and type
        outputItem = {'name':'', 'value':newItem['price'], 'sellXP':newItem['sell_xp'], 'craftXP':newItem['craft_xp'],
                      'type':'', 'level':newItem['level'], 'repairCost':newItem['repair_cost'],
                      'picLink':cdnBase+newItem['image'], 'id':newItem['id']}
        # the usual, grab the name id
        nameID = newItem['name_id']
        # and find it in assets
        for asset in assets:
            if asset['id'] == nameID:
                outputItem['name'] = asset['value']
        # the type for items is stored as a bitmask, just like customers, though it'll always be a single type of course
        # see the getCats function for an explanation of how/why this works
        iType = getCats(newItem['type'])
        # this length check is because rare resources are in 'items', and they won't get a type from the mask
        if len(iType) > 0:
            outputItem['type'] = iType[0]
        else:
            outputItem['type'] = 'rare resource'
        # return the change status and the new item
        return [change[1], outputItem]

    elif changeType == 'recipes':
        ''' example recipe:
        {u'worker_codename': u'druid', u'uid': u'80de6bf22b9f3563efa4fa06a71d2469', u'crafting_time': 5,
        u'__type__': u'Recipe', u'module_level': 6, u'components': [{u'index': 1, u'resource_id': 0,
        u'__type__': u'RecipeComponent', u'recipe_id': 561, u'item_id': 454, u'id': 1884, u'quantity': 1},
        {u'index': 2, u'resource_id': 0, u'__type__': u'RecipeComponent', u'recipe_id': 561, u'item_id': 451,
        u'id': 1885, u'quantity': 2}, {u'index': 3, u'resource_id': 0, u'__type__': u'RecipeComponent',
        u'recipe_id': 561, u'item_id': 563, u'id': 1886, u'quantity': 1}, {u'index': 4, u'resource_id': 15,
        u'__type__': u'RecipeComponent', u'recipe_id': 561, u'item_id': 0, u'id': 1887, u'quantity': 10}],
        u'item_id': 561, u'module_id': 54, u'id': 561}
        '''
        # grab the new recipe
        newRecipe = change[2]
        allItems = newSD['items']
        # fill out the easy stuff
        outputRecipe = {'name':'', 'madeBy':'', 'craftTime':ctimeConverter[newRecipe['crafting_time']], 'madeOn':[],
                        'ingredients':[], 'type':'', 'id':newRecipe['id'],
                        'craftTimeNum':ctimeFloatConverter[newRecipe['crafting_time']]}
        # get the item name and type from the items section
        for item in allItems:
            if item['id'] == newRecipe['id']:
                iNameID = item['name_id']
                iTypeNum = item['type']
        for asset in assets:
            if asset['id'] == iNameID: outputRecipe['name'] = asset['value']
        # since it's a specific item, there will only be one result from the type list, so just grab that
        outputRecipe['type'] = getCats(iTypeNum)[0]
        # if it's not a rare resource (only rare resources have a 0 for module_id);
        if newRecipe['module_id'] != 0:
            # go through classes to get the name for madeBy
            for cclass in newSD['character_classes']:
                if cclass['codename'] == newRecipe['worker_codename']:
                    clNameID = cclass['name_id']
            # go through modules to the the name and level for madeOn
            for module in newSD['modules']:
                if module['id'] == newRecipe['module_id']:
                    modNameID = module['name_id']
                    modLevel = module['power']
            # then get the names from assets
            for asset in assets:
                if asset['id'] == clNameID: outputRecipe['madeBy'] = asset['value']
                elif asset['id'] == modNameID: outputRecipe['madeOn'] = [asset['value'], newRecipe['module_level']]
            # finally, get the ingredients
            for thing in newRecipe['components']:
                # need the name and amount; amount is easy, so get the name first
                # exactly one of item_id and resource_id will be nonzero, which determines the type
                if thing['item_id'] != 0:
                    for item in allItems:
                        if item['id'] == thing['item_id']: thingNameID = item['name_id']
                else:
                    for res in newSD['resources']:
                        if res['id'] == thing['resource_id']: thingNameID = res['name_id']
                for asset in assets:
                    if asset['id'] == thingNameID: outputRecipe['ingredients'].append([thing['quantity'], asset['value']])
        # otherwise, set madeBy and madeOn to 'none', as well as 'ingredients'
        else:
            outputRecipe['madeBy'] = 'none'
            outputRecipe['madeOn'] = 'none'
            outputRecipe['ingredients'] = 'none'
        return [change[1], outputRecipe]

    elif changeType == 'modules':
        ''' example module:
        {u'uid': u'7a24f807012e39da720f8a56ed1de55a', u'disabled': False, u'resource_codename': u'raw_mithril',
        u'id': 150, u'max_upgrade_level': 5, u'resource_modifiers': [{u'while_building': False, u'is_global': True,
        u'__type__': u'Modifier', u'add': 17.0, u'id': 0, u'iso_y': 0.0, u'iso_x': 0.0, u'radius': 0.0,
        u'hidden': False, u'overwrites': False, u'modifies': u'resource.max_count.raw_mithril', u'mult': 0.0},
        {u'while_building': False, u'is_global': True, u'__type__': u'Modifier', u'add': 18.0, u'id': 0, u'iso_y': 0.0,
        u'iso_x': 0.0, u'radius': 0.0, u'hidden': False, u'overwrites': False,
        u'modifies': u'resource.max_count.raw_mithril', u'mult': 0.0}, {u'while_building': False, u'is_global': True,
        u'__type__': u'Modifier', u'add': 19.0, u'id': 0, u'iso_y': 0.0, u'iso_x': 0.0, u'radius': 0.0,
        u'hidden': False, u'overwrites': False, u'modifies': u'resource.max_count.raw_mithril', u'mult': 0.0},
        {u'while_building': False, u'is_global': True, u'__type__': u'Modifier', u'add': 20.0, u'id': 0, u'iso_y': 0.0,
        u'iso_x': 0.0, u'radius': 0.0, u'hidden': False, u'overwrites': False,
        u'modifies': u'resource.max_count.raw_mithril', u'mult': 0.0}, {u'while_building': False, u'is_global': True,
        u'__type__': u'Modifier', u'add': 22.0, u'id': 0, u'iso_y': 0.0, u'iso_x': 0.0, u'radius': 0.0,
        u'hidden': False, u'overwrites': False, u'modifies': u'resource.max_count.raw_mithril', u'mult': 0.0}],
        u'__type__': u'Module', u'parent_id': 45, u'astar_nodes': [], u'name_id': 26679, u'codename': u'bin_mithril',
        u'icon': u'shopr2/shop/icons/magic_bin_mithril_t.png', u'type': 512, u'power': 4, u'pois': [],
        u'scene_objects': [{u'image_path': u'magic_bin_mithril', u'nb_automated_frames': 0, u'edition_type': 5,
        u'id': 150, u'__type__': u'SceneObject', u'iso_y_offset': 0, u'iso_x_offset': 0, u'animation': None,
        u'y_offset': -115, u'iso_height': 2, u'iso_width': 2, u'x_offset': -40, u'module_id': 150, u'children': [],
        u'animation_speed': 1.0}], u'shop_appeals': None, u'modifiers': [], u'unlock_fame_level': 1, u'maximum': 3,
        u'costs': [-1, -1, -1, -1, -1], u'build_times': [345600, 432000, 864000, 1080000, 1296000], u'hammer_cost': 250}
        '''
        # get the new module
        newModule = change[2]
        # set the easy stuff first
        outputModule = {'name':'', 'tier':newModule['power'], 'goldCosts':newModule['costs'],
                        'hammerCost':newModule['hammer_cost'], 'times':newModule['build_times'],
                        'maxBuyable':newModule['maximum'], 'levelReq':newModule['unlock_fame_level'],
                        'appeals':newModule['shop_appeals'], 'unlockedBy':'', 'bonuses':[],
                        'picLink':cdnBase+newModule['icon'], 'id':newModule['id']}
        # get the name
        for asset in assets:
            if asset['id'] == newModule['name_id']: outputModule['name'] = asset['value']
        # get parent module name, if there is one (otherwise unlcokedBy = 'none')
        if newModule['parent_id'] != 0:
            # go through all the modules
            for mod in newSD['modules']:
                # find the one that matches the parent id
                if mod['id'] == newModule['parent_id']:
                    # get teh name id
                    pmodNameID = mod['name_id']
                    # and get the name from assets
                    for asset in assets:
                        if asset['id'] == pmodNameID: outputModule['unlockedBy'] = asset['value']
        else: outputModule['unlockedBy'] = 'none'
        # grab all the bonuses; only one of 'modifiers' and 'resource_modifiers' will have anything in it; if they're
        # both empty, no 'bonuses' are provided
        if len(newModule['resource_modifiers']) > 0:
            # for 'resource_modifiers', the capacity for each level is stored in a separate 'resource_modifier' object,
            # and the resource it modifies is stored in each one in 'modifies'
            # so just grab one of the 'modifies'
            what = newModule['resource_modifiers'][0]['modifies']
            # and go through each modifier and get 'add', and put it in a list
            bonusList = [x['add'] for x in newModule['resource_modifiers']]
            # and set bonuses to [what, thatList]
            outputModule['bonuses'].append([what, bonusList])
        elif len(newModule['modifiers']) > 0:
            # for 'modifiers', 'add' is the base bonus that tier provides, and each level of the module (including the
            # first) adds the value in 'add_level'
            # the what is still stored in 'modifies'
            # so for each modifier, which provides a different bonus:
            for mod in newModule['modifiers']:
                # some modifiers don't have 'add' and some don't have 'base', but the end formula is still the same
                # so just check for each and set them
                if 'add' in mod: base = mod['add']
                else: base = 0
                if 'add_level' in mod: add = mod['add_level']
                else: add = 0
                what = mod['modifies']
                bonusList = []
                # now, we want a list of the bonus at each level of this module, which is base + add*level
                for i in xrange(newModule['max_upgrade_level']):
                    bonusList.append(base+add*(i+1))
                # append the what and bonusList to the 'bonuses' key for each modifier present
                outputModule['bonuses'].append([what, bonusList])
        return [change[1], outputModule]

    elif changeType == 'quests':
        '''
        {u'worker_codename': None, u'party_members': [{u'index': 0, u'codename': u'archer',
        u'__type__': u'QuestPartyMember'}, {u'index': 1, u'codename': u'soldier', u'__type__': u'QuestPartyMember'},
        {u'index': 2, u'codename': u'archer', u'__type__': u'QuestPartyMember'}], u'customer_xp_reward': 912,
        u'npc_intro_id': 25611, u'__type__': u'Quest', u'npc': u'npc_ranger', u'id': 17, u'parent_id': 16,
        u'party_items': [{u'item_id': 300, u'index': 0, u'__type__': u'QuestPartyItem', u'item_type_mask': 0},
        {u'item_id': 7, u'index': 1, u'__type__': u'QuestPartyItem', u'item_type_mask': 0}, {u'item_id': 115,
        u'index': 2, u'__type__': u'QuestPartyItem', u'item_type_mask': 0}], u'name_id': 25610,
        u'npc_conclusion_id': 25612, u'duration': 216000, u'improvement_id': 0, u'fame_level': 19,
        u'image': u'shopr2/quests/kurtey.png', u'loot': {u'resource_id': 0, u'__type__': u'QuestLoot',
        u'special_item': None, u'amount': 3, u'recipe_id': 0, u'item_id': 25}}
        '''
        # get the new quest
        newQuest = change[2]
        # fill out the easy stuff
        outputQuest = {'name':'', 'introText':'', 'outroText':'', 'time':newQuest['duration']/3600,
                       'shopLevelReq':newQuest['fame_level'], 'picLink':cdnBase+newQuest['image'], 'unlockedBy':'none',
                       'custsNeeded':[], 'itemsNeeded':[], 'reward':[], 'xp':newQuest['customer_xp_reward'],
                       'id':newQuest['id']}
        # get the easy text IDs
        nameTextID = newQuest['name_id']
        introTextID = newQuest['npc_intro_id']
        outroTextID = newQuest['npc_conclusion_id']
        for asset in assets:
            if asset['id'] == nameTextID: outputQuest['name'] = asset['value']
            elif asset['id'] == introTextID: outputQuest['introText'] = asset['value']
            elif asset['id'] == outroTextID: outputQuest['outroText'] = asset['value']
        # if the quest has a parent id, get the name of the previous quest in the line
        if newQuest['parent_id'] != 0:
            for quest in newSD['quests']:
                if quest['id'] == newQuest['parent_id']: pnameTextID = quest['name_id']
            for asset in assets:
                if asset['id'] == pnameTextID: outputQuest['unlockedBy'] = asset['value']
        # get the customer classes needed
        for cust in newQuest['party_members']:
            for cclass in newSD['character_classes']:
                if cclass['codename'] == cust['codename']:
                    for asset in assets:
                        if asset['id'] == cclass['name_id']: outputQuest['custsNeeded'].append(asset['value'])
        # get the items needed
        for reqItem in newQuest['party_items']:
            for item in newSD['items']:
                if item['id'] == reqItem['item_id']:
                    for asset in assets:
                        if asset['id'] == item['name_id']: outputQuest['itemsNeeded'].append(asset['value'])
        # get the reward info; only one of resource_id, item_id, and special_item will be nonzero/nonNone
        if newQuest['loot']['resource_id'] != 0:
            resID = newQuest['loot']['resource_id']
            for res in newSD['resources']:
                if res['id'] == resID: rewardTextID = res['name_id']
        elif newQuest['loot']['item_id'] != 0:
            itemID = newQuest['loot']['item_id']
            for i in newSD['items']:
                if i['id'] == itemID: rewardTextID = i['name_id']
        else:
            rewardTextID = 0
            outputQuest['reward'] = [newQuest['loot']['amount'], newQuest['loot']['special_item']]
        # if the reward isn't a special item, get the name text from assets
        if rewardTextID != 0:
            for asset in assets:
                if asset['id'] == rewardTextID: outputQuest['reward'] = [newQuest['loot']['amount'], asset['value']]
        return [change[1], outputQuest]

    elif changeType == 'workers':
        '''
        {u'character_class_id': 20, u'uid': u'b2436e9a95f3424c8ee88aec195d7b62', u'ticket_cost': 3, u'color': 0,
        u'__type__': u'Worker', u'unlock_improvement_id': 0, u'cost': 10000, u'unlock_shop_fame': 14, u'id': 6}
        '''
        # get the new worker
        newWorker = change[2]
        # fill out the easy stuff
        outputWorker = {'name':'', 'goldCost':newWorker['cost'], 'couponCost':newWorker['ticket_cost'],
                        'shopLevelReq':newWorker['unlock_shop_fame'], 'id':newWorker['id']}
        # get the class name id
        for cclass in newSD['character_classes']:
            if cclass['id'] == newWorker['character_class_id']:
                for asset in assets:
                    if asset['id'] == cclass['name_id']: outputWorker['name'] = asset['value']
        return [change[1], outputWorker]

    elif changeType == 'achievements':
        '''
        {u'index': 0, u'rewards': [{u'__type__': u'AchievementReward', u'type': 2, u'id': 166, u'data': u'greatmace'}],
        u'description_id': 26350, u'image': None, u'gamename': u'shopr2', u'__type__': u'Achievement', u'flags': 14,
        u'parent_id': 482, u'name_id': 26349, u'limit': 100, u'type': 13, u'id': 483}
        '''
        # get the new achievement
        newAchievement = change[2]
        # fill out the easy stuff
        outputAchievement = {'name':'', 'requrement':'', 'reward':[]}
        # get the name and description text from assets
        for asset in assets:
            if asset['id'] == newAchievement['name_id']: outputAchievement['name'] = asset['value']
            elif asset['id'] == newAchievement['description_id']: outputAchievement['requirement'] = asset['value']
        if newAchievement['rewards'][0]['type'] == 2 or newAchievement['rewards'][0]['type'] == 7:
            outputAchievement['reward'] = newAchievement['rewards'][0]['data']
        else:
            typeDict = {1:'gold', 3:'platinum hammer', 4:'mystical hourglass', 5:'starry coupon', 6:'magical key',
                        8:'mithril gear'}
            outputAchievement['reward'] = [newAchievement['rewards'][0]['data'],
                                           typeDict[newAchievement['rewards'][0]['type']]]
        return [change[1], outputAchievement]

    elif changeType == 'character_classes':
        '''
        {u'bust_image': u'shopr2/characters/heads/monk_female_head.png', u'uid': u'6c827afdc52d3213b8711fcd62766a70',
        u'sprite_collection': u'monk_f_spritesheet', u'description_id': 0, u'gender': False,
        u'full_image': u'shopr2/characters/full/portrait_monk_female.png', u'__type__': u'CharacterClass',
        u'name_id': 27058, u'y_offset': -200, u'x_offset': -125, u'codename': u'monk', u'id': 45,
        u'items_mask': 522489864}
        '''
        # get the new character class
        newCClass = change[2]
        # fill out the easy stuff
        outputCClass = {'name':'none', 'description':'none', 'icon':cdnBase+newCClass['bust_image'],
                        'fullPic':cdnBase+newCClass['full_image'], 'klashItems':'(not a klasher)', 'id':newCClass['id']}
        # any of name, description, and klash items (items_mask) could be zero, so just check each
        if newCClass['name_id'] != 0:
            for asset in assets:
                if asset['id'] == newCClass['name_id']: outputCClass['name'] = asset['value']
        if newCClass['description_id'] != 0:
            for asset in assets:
                if asset['id'] == newCClass['description_id']: outputCClass['description'] = asset['value']
        if newCClass['items_mask'] != 0: outputCClass['klashItems'] = getCats(newCClass['items_mask'])
        return [change[1], outputCClass]

    elif changeType == 'krown_rewards':
        '''
        {u'level': 0, u'amounts': u'4', u'prize_index': 2, u'__type__': u'KrownReward', u'type': 1, u'id': 3,
        u'prize_uid': u'rareitem_volcanic_rock'}
        '''
        # get the new chest reward
        newChest = change[2]
        # fill out the easy stuff
        outputChest = {'kounter':newChest['level']+1, 'id':newChest['id']}
        if newChest['type'] == 2: outputChest['prize'] = [newChest['amounts'], 'krowns']
        else: outputChest['prize'] = [newChest['amounts'], newChest['prize_uid']]
        return [change[1], outputChest]

    elif changeType == 'fullItems':
        # a fullItem will just be the id of an item, which will be used to get all possible info about the item
        achievementDict = {'plateoftherenown': 545, 'strong_herbs': 242, 'solaxe': 58, 'frostshuriken': 342,
                           'belial': 74, 'grandmasterrobe': 183, 'heavyhelmet': 91, 'silverhelmet': 161,
                           'clericalmark': 456, 'smithgloves': 144, 'masterhat': 217, 'stormpendant': 471,
                           'retribution': 453, 'sorceryring': 485, 'compoundcrossbow': 310, 'shockdarts': 331,
                           'blazepartisan': 417, 'phoenixflute': 372, 'greatmace': 386, 'nexus': 452, 'templarsword': 9,
                           'dragonheart': 35, 'warriorsabaton': 105, 'knightgauntlets': 85, 'sharpshooter': 320,
                           'blackout': 346, 'trustylance': 408, 'mithrilriviera': 424, 'selfbow': 297, 'leafbow': 303,
                           'celestialharp': 357, 'dragonpipes': 367, 'clericrobe': 173, 'elvenvambrace': 203,
                           'softboots': 134, 'divineleather': 124, 'ringofkings': 497, 'dusttriad': 249,
                           'skillburr': 255, 'energydrink': 264, 'acidvial': 270, 'firestormscroll': 284,
                           'shellscroll': 289, 'anubis': 445, 'viperband': 494, 'epicdefender': 549, 'masamune': 548,
                           'apocaplypticstaff': 550}
        itemID = change[2]
        for item in newSD['items']:
            if item['id'] == itemID: itemObj = item
        postCraftObjs = []
        for recipe in newSD['recipes']:
            if recipe['id'] == itemID: recipeObj = recipe
            for ingr in recipe['components']:
                if ingr['item_id'] == itemID: postCraftObjs.append(recipe)
        nextItemObj = None
        prevItemObj = None
        for recUnlock in newSD['recipe_unlocks']:
            if recUnlock['crafted_item_id'] == itemID: nextItemObj = recUnlock
            if recUnlock['recipe_id'] == itemID: prevItemObj = recUnlock
        buildingObjs = []
        for impr in newSD['improvements']:
            for req in impr['requirements']:
                if req['item_id'] == itemID: buildingObjs.append(impr)
        questObjs = []
        for quest in newSD['quests']:
            for i in quest['party_items']:
                if i['item_id'] == itemID: questObjs.append(quest)
        item = getInfo(['items', 'new version', itemObj], newSD)[1]
        recipe = getInfo(['recipes', 'new version', recipeObj], newSD)[1]
        postCrafts = []
        for x in postCraftObjs: postCrafts.append(getInfo(['recipes', 'new version', x], newSD)[1])
        if nextItemObj is not None: nextItem = getInfo(['recipe_unlocks', 'new version', nextItemObj], newSD)[1]
        else: nextItem = '--'
        prevItemType = 'item'
        if prevItemObj is not None: prevItem = getInfo(['recipe_unlocks', 'new version', prevItemObj], newSD)[1]
        else:
            prevItem = None
            for achievement in newSD['achievements']:
                if achievement['rewards'][0]['type'] == 2:
                    if achievementDict[achievement['rewards'][0]['data']] == item['id']:
                        prevItem = getInfo(['achievements', 'new version', achievement], newSD)[1]
                        prevItemType = 'achievement'
            if prevItem is None: prevItem = '--' ### check cheevo dict before setting this blank
        buildings = []
        for x in buildingObjs: buildings.append(getInfo(['improvements', 'new version', x], newSD)[1])
        quests = []
        for x in questObjs: quests.append(getInfo(['quests', 'new version', x], newSD)[1])
        item.update(recipe)
        if nextItem != '--': item['nextItem'] = [nextItem['itemUnlocked'], nextItem['itemToCraft'][1]]
        else: item['nextItem'] = nextItem
        if prevItem != '--':
            if prevItemType == 'achievement': item['prevItem'] = prevItem['name']
            else: item['prevItem'] = prevItem['itemToCraft']
        else: item['prevItem'] = prevItem
        item['nfRecs'] = []
        if len(postCrafts) > 0:
            for x in postCrafts: item['nfRecs'].append(x['name'])
        else: item['nfRecs'].append('--')
        item['nfQuests'] = []
        if len(quests) > 0:
            for x in quests: item['nfQuests'].append(x['name'])
        else: item['nfQuests'].append('--')
        item['nfBuilds'] = []
        if len(buildings) > 0:
            for x in buildings: item['nfBuilds'].append([x['name'], x['level'], x['upgradeCost'][0]])
        else: item['nfBuilds'].append('--')
        return [change[1], item]

    else:
        return change
