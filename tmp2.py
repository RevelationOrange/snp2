import snp2lib
import json


initString = ''

sdd = snp2lib.getSDdict()
items = sdd['items']
recipes = sdd['recipes']
assets = sdd['assets']
derp = json.loads(initString)
invyByType = {}
invyList = derp['result']['player']['item_instances']
raresCount = {}
raresList = []
i = 0
for entry in invyList:
    item = items[str(entry['item_id'])]
    itype = item['type']
    inameid = item['name_id']
    ct = entry['count']
    if itype != snp2lib.rareTypeNum: i += ct
    if itype in invyByType: invyByType[itype].append([inameid, ct])
    else: invyByType[itype] = [[inameid, entry['count']]]
    for ingr in recipes[str(entry['item_id'])]['components']:
        iid = ingr['item_id']
        if iid != 0:
            if items[str(iid)]['type'] == snp2lib.rareTypeNum:
                raresList.append([iid, ingr['quantity']*ct])
                if iid not in raresCount: raresCount[iid] = 0

for r in raresList:
    raresCount[r[0]] += r[1]

for type in invyByType:
    typeStr = snp2lib.getCats(type)[0]
    print '{}:'.format(typeStr)
    for entry in invyByType[type]:
        print '{} x{}'.format(assets[str(entry[0])]['value'], entry[1])
    print ''
print i, 'items total'

for iid in raresCount:
    rareName = assets[str(items[str(iid)]['name_id'])]['value']
    print '{:<16} x{}'.format(rareName, raresCount[iid])
