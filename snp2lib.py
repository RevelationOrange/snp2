from itertools import compress


'''
snp2lib will hold any function that might be useful later on (not just for dealing with the static dump)
for now, it's mainly for getInfo, which will deal with customers, city improvements, etc. found in a difference check
'''

# this is the base url for getting images and such from edgebee
# along with a type version because it's easier
cdnBase = "cdn.edgebee.com/static/"
cndBase = cdnBase

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

def getInfo(change=0, newSD=0):
    # getInfo is the master function to determine the type of change in the static dump and all the info about it
    # currently works for: customers (sans color), quests
    # maybe change it later so each case is a separate function and store them in a dict? who knows

    # default return when given no arguments is a list of change types accepted
    if change == 0:
        return ['customers', 'hunts', 'items', 'improvements']

    # if the main dict was passed as newSD, bypass that silly 'result' key
    if 'result' in newSD:
        newSD = newSD['result']

    # catlist is the ordered list of item categories, for use with customer item masks
    # it's used in a few cases, so it needs to be defined here
    catList = maskList( ['swords', 'axes', 'maces', 'spears', 'daggers', 'staves', 'bows', 'music', 'thrown', 'guns',
                         'heavy armor', 'armor', 'clothes', 'heavy helmets', 'helmets', 'hats', 'gauntlets', 'gloves',
                         'bracers', 'heavy boots', 'boots', 'shoes', 'shields', '', 'potions', 'herbs', 'scrolls',
                         'rings', 'amulets'] )

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

        # and now to deal with the items mask
        # first the value must be converted to a binary number, which, when using bin(), actually makes it a string for
        # some reason, with '0b' at the beginning, so we use element 2 to the end to only get the actual number
        # then, we need to reverse the number; as stored, the 2^0 bit corresponds to swords, so we want that to always
        # be the first digit
        # then just convert each thing to int (since at that point they're all still characters), and save it to mask
        mask = [int(y) for y in reversed([x for x in bin(iMask)][2:]) ]
        # finally, use the mask on the category list and story in the customer's iTypes
        outputCust['iTypes'] = catList[mask]
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
                       'time':newHunt['duration']/3600, 'shopLvlReq':newHunt['unlock_fame_level'],
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
        pass
    elif changeType == 'customer_level_values':
        pass
    elif changeType == 'recipe_unlocks':
        pass
    elif changeType == 'assets':
        pass
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
        # see the customers section for an explanation of how/why this works
        typeMask = newItem['type']
        mask = [int(y) for y in reversed([x for x in bin(typeMask)][2:]) ]
        iType = catList[mask]
        # this length check is because rare resources are in 'items', and they won't get a type from the mask
        if len(iType) > 0:
            outputItem['type'] = iType[0]
        else:
            outputItem['type'] = 'rare resource'
        # return the change status and the new item
        return [change[1], outputItem]
    elif changeType == 'recipes':
        '''
        {u'worker_codename': u'druid', u'uid': u'80de6bf22b9f3563efa4fa06a71d2469', u'crafting_time': 5,
        u'__type__': u'Recipe', u'module_level': 6, u'components': [{u'index': 1, u'resource_id': 0,
        u'__type__': u'RecipeComponent', u'recipe_id': 561, u'item_id': 454, u'id': 1884, u'quantity': 1},
        {u'index': 2, u'resource_id': 0, u'__type__': u'RecipeComponent', u'recipe_id': 561, u'item_id': 451,
        u'id': 1885, u'quantity': 2}, {u'index': 3, u'resource_id': 0, u'__type__': u'RecipeComponent',
        u'recipe_id': 561, u'item_id': 563, u'id': 1886, u'quantity': 1}, {u'index': 4, u'resource_id': 15,
        u'__type__': u'RecipeComponent', u'recipe_id': 561, u'item_id': 0, u'id': 1887, u'quantity': 10}],
        u'item_id': 561, u'module_id': 54, u'id': 561}
        '''
        pass
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
        pass
