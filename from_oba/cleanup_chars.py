import json
import codecs

catlist=['swords', 'axes', 'maces', 'spears', 'daggers', 'staves', 'bows', 'music', 'thrown', 'guns',
                         'heavy armor', 'armor', 'clothes', 'heavy helmets', 'helmets', 'hats', 'gauntlets', 'gloves',
                         'bracers', 'heavy boots', 'boots', 'shoes', 'shields', '', 'potions', 'herbs', 'scrolls',
                         'rings', 'amulets', 'rare resources']

# adapted from Revelation Orange github
def getCats(iMask):
	# item types are stored in a bit of a strange way: as a bitmask corresponding to the category list:

	# the items_mask value must be converted to a binary number, which, when using bin(), actually makes it a string for
	# some reason, with '0b' at the beginning, so we use element 2 to the end to only get the actual number
	# then, we need to reverse the number; as stored, the 2^0 bit corresponds to swords, so we want that to always
	# be the first digit
	# then just convert each thing to int (since at that point they're all still characters), and save it to mask
	mask = [ int(y) for y in reversed([x for x in bin(iMask)][2:]) ]
	#print(mask)
	res=[]
	for i in range(0,len(mask)):
		if (mask[i]==1):
			res.append(catlist[i])
	# apply the mask to the category list and return it
	return res

path=r'chars.json'

f=codecs.open(r'assets_clean.json' , "r" , "UTF-8")
dat=f.read()
f.close()
assets=json.loads(dat)

f=codecs.open(r'class_info_table.json' , "r" , "UTF-8")
dat=f.read()
f.close()
old_chars=json.loads(dat)

f=codecs.open(path , "r" , "UTF-8")
dat=f.read()
f.close()
jsnptr=json.loads(dat)

'''
"bust_image": "shopr2/characters/heads/vendorcute_female_head.png",
"uid": "addc1ada887849213bc44a43c0157dcc",
"sprite_collection": "vendor_cute_f_spritesheet",
"description_id": 0,
"gender": false,
"full_image": "shopr2/characters/full/portrait_vendor_cute_female.png",
"__type__": "CharacterClass",
"name_id": 0,
"y_offset": -200,
"x_offset": -125,
"codename": "npc_cute_f",
"id": 1,
"items_mask": 0
'''

res={}
for item in jsnptr:
	if (item["items_mask"]>0):
		tmp={}
		tmp["icon"]=item["bust_image"].replace("shopr2/characters/heads/" , "/heads/")
		tmp["items_mask"]=item["items_mask"]
		tmp["items"]=getCats(item["items_mask"])
		if (item["name_id"]>0):
			tmp["type_name"]=assets[str(item["name_id"])]
		else:
			tmp["type_name"]=""
		if (str(item['id']) in old_chars):
			tmp["customer_category"]=old_chars[str(item['id'])]["customer_category"]
		res[item['id']]=tmp
encodeditems=json.dumps(res)

res=codecs.open(r'chars_mask_clean.json' , "w" , "UTF-8")
res.write(encodeditems)
res.close()