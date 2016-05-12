import snp2lib
import json


inFileName = 'inventory.txt'
with open(inFileName) as invyFile:
    for line in invyFile: initString = line

outFileName = 'inventoryCount.txt'
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

with open(outFileName, 'w') as invyOutput:
    for type in invyByType:
        typeStr = snp2lib.getCats(type)[0]
        invyOutput.write('{}:\n'.format(typeStr))
        for entry in invyByType[type]:
            invyOutput.write('{} x{}\n'.format(assets[str(entry[0])]['value'], entry[1]))
        invyOutput.write('\n')
    invyOutput.write(str(i) + ' items total\n\n')

    for iid in sorted(raresCount):
        rareName = assets[str(items[str(iid)]['name_id'])]['value']
        invyOutput.write('{:<16} x{}\n'.format(rareName, raresCount[iid]))
