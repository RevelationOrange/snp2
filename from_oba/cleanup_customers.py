import json
import codecs

path=r'customers.json'

f=codecs.open(r'assets_clean.json' , "r" , "UTF-8")
dat=f.read()
f.close()
assets=json.loads(dat)

f=codecs.open(r'chars_clean.json' , "r" , "UTF-8")
dat=f.read()
f.close()
chars=json.loads(dat)

f=codecs.open(path , "r" , "UTF-8")
dat=f.read()
f.close()
jsnptr=json.loads(dat)


res={}
for item in jsnptr:
	tmp={}
	tmp["type_id"]=item["character_class_id"]
	tmp["items_mask"]=item["items_mask"]
	tmp["max_level"]=item["max_level"]
	if (item["name_id"]>0):
		tmp["customer_name"]=assets[str(item["name_id"])]
	else:
		tmp["customer_name"]=""
	
	res[item['id']]=tmp
encodeditems=json.dumps(res)

res=codecs.open(r'customers_clean.json' , "w" , "UTF-8")
res.write(encodeditems)
res.close()