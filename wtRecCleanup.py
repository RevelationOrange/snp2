import json
import snp2lib
from os import sep


wtSetsClean = []
folder = 'townInfo'
inputFileNames = 'wtRecs2.txt'
outFilename = inputFileNames.split('.')[0] + 'cleaned.txt'
print outFilename
sdd = snp2lib.getSDdict()
items = sdd['items']
assets = sdd['assets']

save = True

fn = inputFileNames
with open(folder+sep+fn) as inputFile:
    for line in inputFile:
        derp = json.loads(line)
        if 'result' in derp:
            tmp = derp['result']['events'][0]['world_offers']
            offers = []
            for x in tmp:
                offer = {}
                offer['iid'] = x['item_id']
                offer['ct'] = x['offer_count']
                offer['pr'] = x['unit_price']
                offers.append(offer)
            batch = {'fD':derp['fetchDate'], 'offers':offers}
            wtSetsClean.append(batch)
        else:
            print 'no need to clean'
            break

if save and len(wtSetsClean) > 0:
    with open(folder+sep+outFilename, 'w') as outFile:
        for x in wtSetsClean: outFile.write(json.dumps(x) + '\n')
