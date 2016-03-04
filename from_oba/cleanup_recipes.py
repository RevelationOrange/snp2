import json
import codecs

path=r'recipies.json'

craft_times=[100,200,300,400,700,1000]

f=codecs.open(r'assets_clean.json' , "r" , "UTF-8")
dat=f.read()
f.close()
assets=json.loads(dat)

f=codecs.open(r'items_clean.json' , "r" , "UTF-8")
dat=f.read()
f.close()
items=json.loads(dat)

f=codecs.open(r'resources_clean.json' , "r" , "UTF-8")
dat=f.read()
f.close()
resources=json.loads(dat)

'''
{
			"worker_codename": "blacksmith",
			"uid": "158f5a623984db46cc090c51bf8df1ac",
			"crafting_time": 1,
			"__type__": "Recipe",
			"module_level": 1,
			"components": [{
				"index": 1,
				"resource_id": 1,
				"__type__": "RecipeComponent",
				"recipe_id": 1,
				"item_id": 0,
				"id": 1,
				"quantity": 2
			}],
			"item_id": 1,
			"module_id": 49,
			"id": 1
		}
'''


f=codecs.open(path , "r" , "UTF-8")
dat=f.read()
f.close()
jsnptr=json.loads(dat)

res={}
for item in jsnptr:
	tmp={}
	tmp["worker_codename"]=item["worker_codename"]
	tmp["crafting_time"]=craft_times[item["crafting_time"]]
	tmp["item_id"]=item["item_id"]
	tmp["item_name"]=items[str(item["item_id"])]["name"]
	
	comp=[]
	for component in item["components"]:
		c={}
		if (component["item_id"]>0):
			c["type"]="item"
			c["item_id"]=component["item_id"]
			c["item_name"]=items[str(component["item_id"])]["name"]
		else:
			c["type"]="res"
			c["resource_id"]=component["resource_id"]
			c["resource_name"]=resources[str(component["resource_id"])]["name"]
		c["quantity"]=component["quantity"]
		comp.append(c)
	tmp["components"]=comp
	res[item['id']]=tmp
encodeditems=json.dumps(res)

res=codecs.open(r'recipes_clean.json' , "w" , "UTF-8")
res.write(encodeditems)
res.close()