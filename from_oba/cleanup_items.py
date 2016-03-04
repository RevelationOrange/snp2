import json
import codecs

path=r'items.json'

f=codecs.open(r'assets_clean.json' , "r" , "UTF-8")
dat=f.read()
f.close()
assets=json.loads(dat)
f=codecs.open(path , "r" , "UTF-8")
dat=f.read()
f.close()
jsnptr=json.loads(dat)

res={}
for item in jsnptr:
	tmp={}
	tmp["image"]=item["image"].replace("shopr2/items" , "/item_icons")
	tmp["price"]=item["price"]
	tmp["name"]=assets[str(item["name_id"])]
	tmp["type"]=item["type"]
	tmp["level"]=item["level"]
	tmp["type_str"]=item["type_str"]
	res[item['id']]=tmp
encodeditems=json.dumps(res)

res=codecs.open(r'items_clean.json' , "w" , "UTF-8")
res.write(encodeditems)
res.close()